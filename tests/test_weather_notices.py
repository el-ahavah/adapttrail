import json
import sqlite3
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from app import app, database
from weather import forecast, WeatherUnavailable
from weather_notices import make_notices, parse_preferences, snapshot_current, notice_state
from test_drafts import DraftTests
from test_weather import payload

PLACE = dict(id='1',label='Private test town',latitude=7,longitude=8)


def sample():
    with patch('weather.request_json', return_value=payload()):
        return forecast(PLACE)


class NoticeRulesTests(unittest.TestCase):
    def test_preferences_reject_bad_limits_and_empty_selection(self):
        for limit in ['', 'NaN', 'inf', '-61', '61', 'oops']:
            self.assertTrue(parse_preferences(dict(temperature='yes',temperature_limit=limit))[1])
        self.assertTrue(parse_preferences({})[1])
        self.assertFalse(parse_preferences(dict(rain='yes',temperature_limit='bad'))[1])
        self.assertFalse(parse_preferences(dict(temperature='yes',temperature_limit='0'))[1])

    def test_dates_threshold_equality_precipitation_and_dry_are_distinct(self):
        snap = sample()
        prefs = dict(rain=True,dry=True,temperature=True,temperature_limit=30)
        notices = make_notices(snap,prefs,dict(drainage='poor'))
        self.assertEqual([n['kind'] for n in notices],['rain','temperature'])
        self.assertEqual(notices[0]['dates'],[snap['days'][2]['date']])
        self.assertIn('poor drainage',notices[0]['action'])
        for day in snap['days'][1:]: day['precipitation']=0
        notices = make_notices(snap,prefs,{})
        self.assertEqual([n['kind'] for n in notices],['dry','temperature'])
        self.assertIn('does not establish drought',notices[0]['reason'])
        prefs.update(rain=False,dry=False,temperature_limit=31)
        self.assertEqual(make_notices(snap,prefs,{}),[])

    def test_freshness_age_future_time_and_location_midnight(self):
        snap = sample()
        now = datetime.fromisoformat(snap['retrieved_at'])
        self.assertTrue(snapshot_current(snap, now))
        self.assertFalse(snapshot_current(snap, now+timedelta(hours=6)))
        self.assertFalse(snapshot_current(snap, now-timedelta(seconds=1)))
        now = datetime(2026,10,20,22,30,tzinfo=timezone.utc)
        snap.update(retrieved_at=now.isoformat(),timezone='Africa/Lagos')
        snap['days']=[dict(date=f'2026-10-{i}') for i in range(19,23)]
        self.assertTrue(snapshot_current(snap,now))
        self.assertFalse(snapshot_current(snap,now+timedelta(hours=1)))
        self.assertFalse(snapshot_current(snap|dict(timezone='invalid'),now))
        self.assertIn('failed',notice_state(dict(enabled=True,last_error='error',snapshot=snap)))


class WeatherNoticeFlowTests(unittest.TestCase):
    setUp = DraftTests.setUp
    tearDown = DraftTests.tearDown

    def stored(self):
        connection=database()
        try:return json.loads(connection.execute('SELECT weather_watch FROM drafts WHERE id=1').fetchone()['weather_watch'])
        finally:connection.close()

    def prepare(self):
        self.client.post('/drafts/new',data=self.data)
        with patch('app.search_locations',return_value=[PLACE]):
            self.assertEqual(self.client.post('/drafts/1/weather',data=dict(csrf_token=self.token,intent='search',query='Test town')).status_code,200)
        return dict(csrf_token=self.token,intent='save',location='1',rain='yes',dry='yes',consent='yes')

    def test_login_return_only_accepts_local_weather_pages(self):
        from app import safe_return_path
        self.assertTrue(safe_return_path('/drafts/1/weather'))
        self.assertTrue(safe_return_path('/drafts/1/context'))
        self.assertFalse(safe_return_path('//example.com/drafts/1/weather'))
        self.assertFalse(safe_return_path('/drafts/1/weather/refresh'))

    def test_setup_no_get_network_refresh_persist_and_disable(self):
        data=self.prepare()
        with patch('app.forecast') as fetch:
            self.assertEqual(self.client.post('/drafts/1/weather',data=data).status_code,302)
            self.assertEqual(self.client.get('/drafts/1/weather').status_code,200)
            fetch.assert_not_called()
        snap=sample()
        with patch('app.forecast',return_value=snap):
            self.assertEqual(self.client.post('/drafts/1/weather',data=dict(csrf_token=self.token,intent='refresh')).status_code,302)
        self.assertEqual(self.stored()['snapshot']['retrieved_at'],snap['retrieved_at'])
        page=self.client.get('/drafts/1/weather').data
        self.assertIn(b'Reminders from your last check',page)
        self.assertIn(b'Precipitation in the forecast',page)
        self.assertIn(b'1 reminder from the last check',self.client.get('/drafts/1').data)
        self.client.post('/drafts/1/weather',data=dict(csrf_token=self.token,intent='disable'))
        self.assertEqual(self.stored(),{})
        self.assertNotIn(b'Private test town',self.client.get('/drafts/1/weather').data)
        with patch('app.forecast') as fetch:
            self.assertEqual(self.client.post('/drafts/1/weather',data=dict(csrf_token=self.token,intent='refresh')).status_code,400)
            fetch.assert_not_called()

    def test_invalid_consent_location_threshold_and_csrf_do_not_save(self):
        data=self.prepare()
        for change in [dict(consent=''),dict(location='forged'),dict(csrf_token='bad'),dict(temperature='yes',temperature_limit='NaN')]:
            self.assertEqual(self.client.post('/drafts/1/weather',data=data|change).status_code,400)
            self.assertEqual(self.stored(),{})
        self.client.post('/drafts/new',data=self.data)
        self.assertEqual(self.client.post('/drafts/2/weather',data=data).status_code,400)
        self.client.post('/drafts/1/weather',data=data)
        previous=self.stored()
        self.assertEqual(self.client.post('/drafts/1/weather',data=dict(csrf_token='bad',intent='disable')).status_code,400)
        self.assertEqual(previous,self.stored())

    def test_failure_stale_state_and_settings_change_hide_old_reminders(self):
        data=self.prepare();self.client.post('/drafts/1/weather',data=data)
        with patch('app.forecast',return_value=sample()):
            self.client.post('/drafts/1/weather',data=dict(csrf_token=self.token,intent='refresh'))
        with patch('app.snapshot_current',return_value=False):
            self.assertNotIn(b'Reminders from your last check',self.client.get('/drafts/1/weather').data)
        with patch('app.forecast',side_effect=WeatherUnavailable('outage')):
            self.client.post('/drafts/1/weather',data=dict(csrf_token=self.token,intent='refresh'))
        page=self.client.get('/drafts/1/weather').data
        self.assertIn(b'Could not update weather',page)
        self.assertIn(b'Previous forecast',page)
        self.assertNotIn(b'Reminders from your last check',page)
        self.client.post('/drafts/1/weather',data=data|dict(location='current'))
        self.assertNotIn('snapshot',self.stored())

    def test_changed_project_conditions_require_new_check(self):
        data=self.prepare();self.client.post('/drafts/1/weather',data=data)
        with patch('app.forecast',return_value=sample()):
            self.client.post('/drafts/1/weather',data=dict(csrf_token=self.token,intent='refresh'))
        self.client.post('/drafts/1/context',data=dict(csrf_token=self.token,drainage='poor'))
        page=self.client.get('/drafts/1/weather').data
        self.assertIn(b'Project information changed',page)
        self.assertNotIn(b'Reminders from your last check',page)
        self.assertIn(b'Project information changed',self.client.get('/drafts/1').data)

    def test_concurrent_disable_is_not_overwritten_by_refresh(self):
        data=self.prepare();self.client.post('/drafts/1/weather',data=data)
        snap=sample()
        def disable_during_fetch(location):
            connection=database()
            try:
                with connection:connection.execute("UPDATE drafts SET weather_watch='{}' WHERE id=1")
            finally:connection.close()
            return snap
        with patch('app.forecast',side_effect=disable_during_fetch):
            response=self.client.post('/drafts/1/weather',data=dict(csrf_token=self.token,intent='refresh'))
        self.assertEqual(response.status_code,409)
        self.assertEqual(self.stored(),{})

    def test_owner_and_publication_privacy(self):
        data=self.prepare();self.client.post('/drafts/1/weather',data=data)
        other=app.test_client();other.get('/register')
        with other.session_transaction() as s:token=s['csrf_token']
        other.post('/register',data=dict(csrf_token=token,username='weatherbob',password='long-password-123',confirmation='long-password-123'))
        other.post('/login',data=dict(csrf_token=token,username='weatherbob',password='long-password-123'))
        other.get('/drafts')
        with other.session_transaction() as s:token=s['csrf_token']
        self.assertEqual(other.get('/drafts/1/weather').status_code,404)
        for intent in ['refresh','save','disable','search']:
            self.assertEqual(other.post('/drafts/1/weather',data=data|dict(csrf_token=token,intent=intent)).status_code,404)
        self.assertEqual(app.test_client().get('/drafts/1/weather').status_code,302)
        public=dict(csrf_token=self.token,title='Public story',country='',problem='Problem',action='Action',outcome='',lessons='Lessons',intent='publish',consent='yes')
        saved=self.client.post('/drafts/1/publish',data=public)
        self.assertNotIn(b'Private test town',app.test_client().get(saved.location).data)

    def test_location_labels_escape_and_existing_sqlite_upgrades(self):
        self.client.post('/drafts/new',data=self.data)
        connection=sqlite3.connect(app.config['DATABASE'])
        connection.execute('ALTER TABLE drafts DROP COLUMN weather_watch');connection.commit();connection.close()
        self.assertEqual(self.stored(),{})
        with patch('app.search_locations',return_value=[PLACE|dict(label='<script>town</script>')]):
            response=self.client.post('/drafts/1/weather',data=dict(csrf_token=self.token,intent='search',query='Town'))
        self.assertIn(b'&lt;script&gt;town&lt;/script&gt;',response.data)
        self.assertNotIn(b'<script>town</script>',response.data)


del DraftTests
