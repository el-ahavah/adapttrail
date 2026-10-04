import unittest
from unittest.mock import patch
from datetime import date, timedelta
from weather import forecast, planning_notes, search_locations, WeatherUnavailable
from test_drafts import DraftTests


def payload():
    start = date.today() - timedelta(days=1)
    return dict(timezone='UTC', daily_units=dict(temperature_2m_min='°C', temperature_2m_max='°C', precipitation_sum='mm'),
                daily=dict(time=[(start+timedelta(days=i)).isoformat() for i in range(4)],
                           temperature_2m_min=[20]*4, temperature_2m_max=[30]*4, precipitation_sum=[0,0,4,0]))


class WeatherTests(unittest.TestCase):
    def test_complete_forecast_and_conditional_notes(self):
        place = dict(id='1',label='Otukpo, Nigeria',latitude=7.2,longitude=8.1)
        with patch('weather.request_json', return_value=payload()):
            result = forecast(place)
        self.assertEqual(len(result['days']), 4)
        self.assertEqual(result['days'][0]['kind'], 'Recent model estimate')
        notes = planning_notes('garden-mulch', dict(drainage='poor',growth='seedling'),result)
        self.assertTrue(any('standing water' in note for note in notes))
        self.assertTrue(any('seedlings' in note for note in notes))
        self.assertIn('not a drought prediction',result['limitation'])

    def test_missing_data_and_wrong_units_never_become_zero(self):
        place = dict(latitude=7,longitude=8)
        for change in ['null','unit','short']:
            data=payload()
            if change == 'null': data['daily']['precipitation_sum'][1]=None
            elif change == 'unit': data['daily_units']['precipitation_sum']='inch'
            else: data['daily']['time'].pop()
            with patch('weather.request_json',return_value=data), self.assertRaises(WeatherUnavailable):
                forecast(place)

    def test_location_matches_are_explicit_and_bounded(self):
        with patch('weather.request_json',return_value=dict(results=[dict(id=1,name='Town',country='Country',latitude=0,longitude=0)])):
            self.assertEqual(search_locations('Town')[0]['latitude'],0)
        with patch('weather.request_json',return_value=dict(results=[dict(id=1,latitude=999,longitude=0)])), self.assertRaises(WeatherUnavailable):
            search_locations('Town')


class WeatherFlowTests(unittest.TestCase):
    setUp = DraftTests.setUp
    tearDown = DraftTests.tearDown
    def test_optional_selection_snapshot_and_outage(self):
        from app import database
        from assessment import FIELDS
        import json
        answers={key:'unknown' for key in FIELDS}
        answers.update(csrf_token=self.token,country='',region='',crop='',resources='',weather_query='Otukpo',intent='search_weather')
        place=dict(id='1',label='Otukpo, Nigeria',latitude=7.2,longitude=8.1)
        with patch('app.search_locations',return_value=[place]):
            response=self.client.post('/assess/rainwater',data=answers)
        self.assertEqual(response.status_code,200)
        connection=database()
        self.assertEqual(connection.execute('SELECT COUNT(*) FROM assessments').fetchone()[0],0)
        connection.close()
        with patch('weather.request_json',return_value=payload()):
            saved=self.client.post('/assess/rainwater',data=answers|dict(intent='save',weather_location='1'))
        self.assertEqual(saved.status_code,302)
        page=self.client.get(saved.location).get_data(as_text=True)
        self.assertIn('Otukpo, Nigeria',page)
        self.assertIn('saved snapshot, not a live forecast',page)
        with patch('app.forecast',side_effect=WeatherUnavailable('Weather service unavailable.')):
            saved=self.client.post('/assess/rainwater',data=answers|dict(intent='save',weather_location='1'))
        self.assertEqual(saved.status_code,302)
        self.assertIn(b'Weather service unavailable',self.client.get(saved.location).data)
        self.assertEqual(self.client.post('/assess/rainwater',data=answers|dict(intent='save',weather_location='forged')).status_code,400)
        with patch('app.forecast') as fetch:
            self.client.post('/assess/rainwater',data=answers|dict(intent='save',weather_location=''))
            fetch.assert_not_called()

del DraftTests
