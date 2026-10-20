"""Opt-in hosted smoke check. Only its generated temporary records are removed."""
import secrets
from app import app, database


def verify():
    names = ['check_' + secrets.token_hex(6) for _ in range(2)]
    password = secrets.token_hex(20)
    clients = [app.test_client(), app.test_client()]

    def token(client, path):
        response = client.get(path, base_url='https://localhost')
        assert response.status_code == 200, (path, response.status_code)
        with client.session_transaction() as session:
            return session['csrf_token']

    def post(client, path, data):
        return client.post(path, data=data, base_url='https://localhost')

    try:
        public_client = app.test_client()
        assert b'/static/app.js' in public_client.get('/',base_url='https://localhost').data
        for asset in ['app.js','style.css','landscape.svg']:
            assert public_client.get('/static/' + asset,base_url='https://localhost').status_code == 200
        destination = '/drafts/from-documented/niger-tahoua'
        for client, name in zip(clients, names):
            assert client.get(destination,base_url='https://localhost').status_code == 302
            csrf = token(client, '/register')
            assert post(client, '/register', dict(csrf_token=csrf, username=name,
                password=password, confirmation=password)).status_code == 302
            csrf = token(client, '/login')
            signed_in = post(client, '/login', dict(csrf_token=csrf, username=name,password=password))
            assert signed_in.status_code == 302
            assert signed_in.headers['Location'] == destination
            assert client.get(destination,base_url='https://localhost').status_code == 200
        alice, bob = clients
        csrf = token(alice, '/drafts/new')
        data = dict(csrf_token=csrf, title='Temporary verification draft',
            country='Test country', problem='Test water problem', approach='Measure use',
            conditions='Test only', source_id='')
        saved = post(alice, '/drafts/new', data)
        assert saved.status_code == 302, saved.status_code
        path = saved.headers['Location']
        assert alice.get(path, base_url='https://localhost').status_code == 200
        assert bob.get(path, base_url='https://localhost').status_code == 404
        assert bob.get(path + '/edit', base_url='https://localhost').status_code == 404
        assert bob.get(path + '/delete', base_url='https://localhost').status_code == 404
        csrf_bob = token(bob, '/drafts')
        assert post(bob, path + '/edit', data | dict(csrf_token=csrf_bob)).status_code == 404
        assert post(bob, path + '/delete', dict(csrf_token=csrf_bob, confirm='delete')).status_code == 404
        progress = dict(csrf_token=token(alice, path + '/progress'), entry_date='2026-01-01', observation='Verification observation', measurement='0', unit='litres', metric='Water used', period='One week', entry_type='baseline')
        assert post(alice, path + '/progress', progress).status_code == 302
        assert b'Verification observation' in alice.get(path + '/progress', base_url='https://localhost').data
        assert bob.get(path + '/progress', base_url='https://localhost').status_code == 404
        assert post(bob, path + '/progress', progress | dict(csrf_token=csrf_bob)).status_code == 404
        assert post(alice, path + '/status', dict(csrf_token=progress['csrf_token'],status='ongoing')).status_code == 302
        task_path = path + '/tasks'
        task_data = dict(csrf_token=token(alice, task_path), title='Private verification checklist task')
        assert post(alice, task_path, task_data).status_code == 302
        connection = database()
        try:
            task = connection.execute('SELECT id FROM project_tasks WHERE project_id=?', (int(path.rsplit('/',1)[1]),)).fetchone()
        finally:
            connection.close()
        task_update = task_path + '/' + str(task['id'])
        assert bob.get(task_path, base_url='https://localhost').status_code == 404
        assert post(bob, task_update, dict(csrf_token=csrf_bob,intent='complete')).status_code == 404
        assert post(alice, task_update, dict(csrf_token='bad',intent='complete')).status_code == 400
        for intent, expected in [('complete', b'1 of 1 completed'), ('archive', b'0 of 0 completed'), ('restore', b'1 of 1 completed'), ('reopen', b'0 of 1 completed')]:
            assert post(alice, task_update, dict(csrf_token=task_data['csrf_token'],intent=intent)).status_code == 302
            assert expected in alice.get(task_path,base_url='https://localhost').data
        assert post(alice, task_update, dict(csrf_token=task_data['csrf_token'],intent='edit',title='Updated private checklist task')).status_code == 302
        assert b'Updated private checklist task' in alice.get(task_path,base_url='https://localhost').data
        assert b'Open checklist' in alice.get(path,base_url='https://localhost').data
        print('AdaptTrail hosted checklist verification passed: persistence, editing, completion, archive/restore, CSRF and owner isolation.', flush=True)
        assert post(alice, task_update, dict(csrf_token=task_data['csrf_token'],intent='complete')).status_code == 302
        task_progress = progress | dict(source_task_id=str(task['id']),observation='Linked task observation',entry_type='observation',measurement='',unit='',metric='',period='')
        assert post(alice,path + '/progress',task_progress).status_code == 302
        assert b'Updated private checklist task' in alice.get(path + '/progress',base_url='https://localhost').data
        assert b'Updated private checklist task' in alice.get(path + '/history',base_url='https://localhost').data
        assert b'1 observation' in alice.get(task_path,base_url='https://localhost').data
        assert post(bob,path + '/progress',task_progress | dict(csrf_token=csrf_bob)).status_code == 404
        print('AdaptTrail task observation verification passed: persisted link, source wording, history, counts and ownership.',flush=True)
        from assessment import FIELDS
        context = {key: 'unknown' for key in FIELDS}
        context.update(csrf_token=token(alice, path + '/context'), crop='Private hosted crop', soil='loam')
        assert post(alice, path + '/context', context).status_code == 302
        assert b'value="Private hosted crop"' in alice.get(path + '/assess', base_url='https://localhost').data
        assert bob.get(path + '/context', base_url='https://localhost').status_code == 404
        assert post(bob, path + '/context', context | dict(csrf_token=csrf_bob)).status_code == 404
        assert post(alice, path + '/context', context | dict(soil='invalid')).status_code == 400
        assert b'value="Private hosted crop"' in alice.get(path + '/context', base_url='https://localhost').data
        answers = {key: 'unknown' for key in FIELDS}
        answers.update(csrf_token=token(alice, path + '/assess'), approach='rainwater', country='Test country',region='',crop='',resources='')
        saved_assessment = post(alice, path + '/assess', answers)
        assert saved_assessment.status_code == 302
        assert b'More information needed' in alice.get(saved_assessment.headers['Location'], base_url='https://localhost').data
        result_page = alice.get(saved_assessment.headers['Location'], base_url='https://localhost')
        assert b'Factors you provided' in result_page.data
        assert b'Assess again' in result_page.data
        assert b'Record an observation' in result_page.data
        assert bob.get(saved_assessment.headers['Location'], base_url='https://localhost').status_code == 404
        assert post(alice, path + '/context', context | dict(crop='Changed hosted crop')).status_code == 302
        assert b'Changed hosted crop' not in alice.get(saved_assessment.headers['Location'], base_url='https://localhost').data
        print('AdaptTrail project context verification passed: persistence, prefill, validation, ownership and unchanged assessment snapshots.', flush=True)
        assessment_id = saved_assessment.headers['Location'].rsplit('/',1)[1]
        suggestion_path = path + '/assessments/' + assessment_id + '/tasks/0'
        assert alice.get(suggestion_path,base_url='https://localhost').status_code == 200
        assert bob.get(suggestion_path,base_url='https://localhost').status_code == 404
        suggestion_data = dict(csrf_token=token(alice,suggestion_path),title='Private task from saved guidance')
        imported = post(alice,suggestion_path,suggestion_data)
        assert imported.status_code == 302
        assert b'From saved assessment #' in alice.get(imported.headers['Location'],base_url='https://localhost').data
        assert post(alice,suggestion_path,suggestion_data).status_code == 302
        connection = database()
        try:
            linked = connection.execute('SELECT COUNT(*) AS total FROM project_tasks WHERE source_assessment_id=?', (int(assessment_id),)).fetchone()
            assert linked['total'] == 1
        finally:
            connection.close()
        print('AdaptTrail assessment-to-checklist verification passed: edited task, source link, duplicate protection and ownership.',flush=True)

        maize_answers = answers | dict(approach='garden-mulch',crop='maize',growth='flowering',soil='sandy',water='low')
        maize_saved = post(alice,path + '/assess',maize_answers)
        assert maize_saved.status_code == 302
        maize_page = alice.get(maize_saved.headers['Location'],base_url='https://localhost')
        assert b'Suggested next steps for your conditions' in maize_page.data
        assert b'FAO: Water shortages' in maize_page.data
        import json
        connection = database()
        try:
            maize_id = int(maize_saved.headers['Location'].rsplit('/',1)[1])
            stored = connection.execute('SELECT result FROM assessments WHERE id=?',(maize_id,)).fetchone()
            card = next(c for c in json.loads(stored['result'])['guidance']['cards'] if c['rule']=='maize-sensitive-stage')
        finally:
            connection.close()
        card_path = path + '/assessments/' + str(maize_id) + '/tasks/' + str(card['check_index'])
        assert post(alice,card_path,dict(csrf_token=csrf,title=card['action'])).status_code == 302
        assert bob.get(card_path,base_url='https://localhost').status_code == 404
        assert card['action'].encode() in alice.get(task_path,base_url='https://localhost').data
        print('AdaptTrail explained guidance verification passed: saved maize prompts, source attribution, checklist import and owner isolation.',flush=True)

        assert bob.get(path + '/assess', base_url='https://localhost').status_code == 404
        workspace = alice.get(path, base_url='https://localhost')
        assert b'Your plan' in workspace.data
        assert b'Read latest result' in workspace.data
        assert b'Linked task observation' in workspace.data
        dashboard = alice.get('/drafts', base_url='https://localhost')
        assert dashboard.status_code == 200
        assert b'Your next step starts here.' in dashboard.data
        assert b'Verification observation' in dashboard.data
        assert b'More information needed' in dashboard.data
        assert b'Verification observation' not in bob.get('/drafts', base_url='https://localhost').data
        # Provider connectivity is optional; outages must preserve assessment saving.
        weather_answers = answers | dict(intent='search_weather', weather_query='Otukpo', weather_location='')
        searched = post(alice, path + '/assess', weather_answers)
        assert searched.status_code in (200,400)
        with alice.session_transaction() as saved_session:
            locations = saved_session.get('weather_locations', [])
        if locations:
            weather_answers.update(intent='save',weather_location=locations[0]['id'])
            weather_saved = post(alice,path + '/assess',weather_answers)
            assert weather_saved.status_code == 302
            weather_page = alice.get(weather_saved.headers['Location'],base_url='https://localhost')
            assert weather_page.status_code == 200
            assert bob.get(weather_saved.headers['Location'],base_url='https://localhost').status_code == 404
            if b'Saved weather context' in weather_page.data:
                print('AdaptTrail live weather provider check passed: location search, forecast snapshot and owner-only access.', flush=True)
            else:
                assert b'weather' in weather_page.data.lower()
                print('AdaptTrail weather provider unavailable: assessment fallback passed.', flush=True)
        else:
            print('AdaptTrail weather location service unavailable: optional lookup fallback passed.', flush=True)

        history = alice.get(path + '/history', base_url='https://localhost')
        assert history.status_code == 200
        assert b'Verification observation' in history.data
        assert b'More information needed' in history.data
        assert bob.get(path + '/history', base_url='https://localhost').status_code == 404
        data['title'] = 'Updated verification draft'
        data['csrf_token'] = token(alice, path + '/edit')
        assert post(alice, path + '/edit', data).status_code == 302
        connection = database()
        try:
            row = connection.execute('SELECT title FROM drafts WHERE id = ?', (int(path.rsplit('/', 1)[1]),)).fetchone()
            assert row['title'] == 'Updated verification draft'
        finally:
            connection.close()
        # Synthetic forecast isolates persistence checks from provider availability.
        from unittest.mock import patch
        from datetime import datetime, timedelta, timezone
        from weather import WeatherUnavailable
        weather_path = path + '/weather'
        notice_place = dict(id='fixture',label='Private weather verification town',latitude=7,longitude=8)
        with patch('app.search_locations',return_value=[notice_place]):
            assert post(alice,weather_path,dict(csrf_token=csrf,intent='search',query='Verification town')).status_code == 200
        preferences = dict(csrf_token=csrf,intent='save',location='fixture',rain='yes',dry='yes',consent='yes')
        assert post(alice,weather_path,preferences).status_code == 302
        now = datetime.now(timezone.utc)
        fixture = dict(location=notice_place,timezone='UTC',retrieved_at=now.isoformat(),
                       days=[dict(date=(now.date()+timedelta(days=i)).isoformat(),low=20,high=30,precipitation=2,kind='Forecast') for i in range(-1,3)])
        with patch('app.forecast',return_value=fixture):
            assert post(alice,weather_path,dict(csrf_token=csrf,intent='refresh')).status_code == 302
        notice_page = alice.get(weather_path,base_url='https://localhost')
        assert b'Reminders from your last check' in notice_page.data
        assert b'Precipitation in the forecast' in notice_page.data
        assert bob.get(weather_path,base_url='https://localhost').status_code == 404
        assert post(bob,weather_path,dict(csrf_token=csrf_bob,intent='disable')).status_code == 404
        with patch('app.forecast',side_effect=WeatherUnavailable('Synthetic outage')):
            assert post(alice,weather_path,dict(csrf_token=csrf,intent='refresh')).status_code == 302
        failed_page = alice.get(weather_path,base_url='https://localhost')
        assert b'Could not update weather' in failed_page.data
        assert b'Reminders from your last check' not in failed_page.data
        print('AdaptTrail weather notices verification passed: synthetic forecast persistence, reminder dates, owner isolation and outage handling.',flush=True)

        public = dict(csrf_token=token(alice,path + '/publish'),title='Temporary public test',country='',problem='Test problem',action='Test action',outcome='',lessons='Test lessons',intent='publish',consent='yes')
        published = post(alice,path + '/publish',public)
        assert published.status_code == 302
        visitor = app.test_client()
        assert visitor.get(published.headers['Location'],base_url='https://localhost').status_code == 200
        assert b'Updated private checklist task' not in visitor.get(published.headers['Location'],base_url='https://localhost').data
        assert b'Changed hosted crop' not in visitor.get(published.headers['Location'],base_url='https://localhost').data
        assert b'Private weather verification town' not in visitor.get(published.headers['Location'],base_url='https://localhost').data
        assert post(alice,weather_path,dict(csrf_token=csrf,intent='disable')).status_code == 302
        assert b'Private weather verification town' not in alice.get(weather_path,base_url='https://localhost').data
        print('AdaptTrail weather notices removal and publication privacy verification passed.',flush=True)
        source_id = published.headers['Location'].rsplit('/',1)[1]
        adapt_path = '/drafts/from-community/' + source_id
        adapted = post(bob,adapt_path,dict(csrf_token=token(bob,adapt_path),title='Temporary adaptation',
            country='Test country',problem='Local problem',approach='Local approach',conditions='',
            changes='Private adaptation plan',reason='Private local constraint'))
        assert adapted.status_code == 302
        child_path = adapted.headers['Location']
        assert b'Private adaptation plan' in bob.get(child_path,base_url='https://localhost').data
        assert alice.get(child_path,base_url='https://localhost').status_code == 404
        assert b'Private adaptation plan' not in visitor.get(published.headers['Location'],base_url='https://localhost').data
        assert post(bob,path + '/unpublish',dict(csrf_token=csrf_bob)).status_code == 404
        assert post(alice,path + '/unpublish',dict(csrf_token=public['csrf_token'])).status_code == 302
        assert visitor.get(published.headers['Location'],base_url='https://localhost').status_code == 404
        assert b'no longer publicly available' in bob.get(child_path,base_url='https://localhost').data
        csrf = token(alice, path + '/delete')
        assert alice.get(path, base_url='https://localhost').status_code == 200
        assert post(alice, path + '/delete', dict(csrf_token=csrf, confirm='delete')).status_code == 302
        assert alice.get(path, base_url='https://localhost').status_code == 404
        assert bob.get(child_path,base_url='https://localhost').status_code == 200
        assert post(bob,child_path + '/delete',dict(csrf_token=token(bob,child_path + '/delete'),confirm='delete')).status_code == 302
        for documented_id in ['niger-tahoua','burkina-stone-bunds','nigeria-newmap','ethiopia-calm','bangladesh-floating','india-cool-roofs']:
            assert visitor.get('/projects/' + documented_id,base_url='https://localhost').status_code == 200
        documented_path = '/drafts/from-documented/niger-tahoua'
        documented_saved = post(bob,documented_path,dict(csrf_token=token(bob,documented_path),title='Temporary documented adaptation',
            country='Test country',problem='Local test problem',approach='Trial approach',conditions='',changes='Private external-source change',reason='Local test reason'))
        assert documented_saved.status_code == 302
        documented_child = documented_saved.headers['Location']
        assert b'/projects/niger-tahoua' in bob.get(documented_child,base_url='https://localhost').data
        assert alice.get(documented_child,base_url='https://localhost').status_code == 404
        assessment_form = bob.get(documented_child + '/assess',base_url='https://localhost')
        assert assessment_form.status_code == 200
        assert b'Choose a supported approach' in assessment_form.data
        assert visitor.get('/how-to-use',base_url='https://localhost').status_code == 200
        assert post(bob,documented_child + '/delete',dict(csrf_token=token(bob,documented_child + '/delete'),confirm='delete')).status_code == 302
        csrf = token(alice, '/drafts')
        assert post(alice, '/logout', dict(csrf_token=csrf)).status_code == 302
        assert alice.get('/drafts', base_url='https://localhost').status_code == 302
    finally:
        connection = database()
        try:
            with connection:
                for name in names:
                    connection.execute('DELETE FROM drafts WHERE user_id IN (SELECT id FROM users WHERE username = ?)', (name,))
                    connection.execute('DELETE FROM users WHERE username = ?', (name,))
        finally:
            connection.close()
