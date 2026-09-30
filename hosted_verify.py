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
        for client, name in zip(clients, names):
            csrf = token(client, '/register')
            assert post(client, '/register', dict(csrf_token=csrf, username=name,
                password=password, confirmation=password)).status_code == 302
            csrf = token(client, '/login')
            assert post(client, '/login', dict(csrf_token=csrf, username=name,
                password=password)).status_code == 302
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
        data['title'] = 'Updated verification draft'
        data['csrf_token'] = token(alice, path + '/edit')
        assert post(alice, path + '/edit', data).status_code == 302
        connection = database()
        try:
            row = connection.execute('SELECT title FROM drafts WHERE id = ?', (int(path.rsplit('/', 1)[1]),)).fetchone()
            assert row['title'] == 'Updated verification draft'
        finally:
            connection.close()
        csrf = token(alice, path + '/delete')
        assert alice.get(path, base_url='https://localhost').status_code == 200
        assert post(alice, path + '/delete', dict(csrf_token=csrf, confirm='delete')).status_code == 302
        assert alice.get(path, base_url='https://localhost').status_code == 404
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
