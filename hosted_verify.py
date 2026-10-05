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
        from assessment import FIELDS
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
        assert bob.get(path + '/assess', base_url='https://localhost').status_code == 404
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
        public = dict(csrf_token=token(alice,path + '/publish'),title='Temporary public test',country='',problem='Test problem',action='Test action',outcome='',lessons='Test lessons',intent='publish',consent='yes')
        published = post(alice,path + '/publish',public)
        assert published.status_code == 302
        visitor = app.test_client()
        assert visitor.get(published.headers['Location'],base_url='https://localhost').status_code == 200
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
