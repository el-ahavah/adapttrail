import tempfile
import unittest
from pathlib import Path
from app import app, database


class DraftTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.previous = app.config['DATABASE']
        app.config.update(TESTING=True, DATABASE=str(Path(self.directory.name) / 'test.sqlite3'))
        self.client = app.test_client()
        self.client.get('/register')
        with self.client.session_transaction() as session:
            token = session['csrf_token']
        self.client.post('/register', data=dict(csrf_token=token, username='alice', password='long-password-123', confirmation='long-password-123'))
        self.client.post('/login', data=dict(csrf_token=token, username='alice', password='long-password-123'))
        self.client.get('/drafts/new')
        with self.client.session_transaction() as session:
            self.token = session['csrf_token']
        self.data = dict(csrf_token=self.token, title='<script>alert(1)</script>',
                         country='Nigeria', problem='Limited water', approach='Track use',
                         conditions='', source_id='garden-mulch')

    def tearDown(self):
        app.config['DATABASE'] = self.previous
        self.directory.cleanup()

    def test_save_reopen_and_escape(self):
        response = self.client.post('/drafts/new', data=self.data)
        self.assertEqual(response.status_code, 302)
        connection = database()
        try:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM drafts').fetchone()[0], 1)
        finally:
            connection.close()
        page = self.client.get(response.location).get_data(as_text=True)
        self.assertIn('&lt;script&gt;', page)
        self.assertNotIn('<script>alert', page)
        self.assertIn('Fictional demo source', page)
        self.assertIn('&lt;script&gt;', self.client.get('/drafts').get_data(as_text=True))

    def test_invalid_and_forged_forms_do_not_save(self):
        for changes in [dict(title=''), dict(problem='x' * 3001),
                        dict(source_id='unknown'), dict(csrf_token='wrong')]:
            self.assertEqual(self.client.post('/drafts/new', data=self.data | changes).status_code, 400)
        connection = database()
        try:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM drafts').fetchone()[0], 0)
        finally:
            connection.close()

    def test_edit_updates_same_record_and_invalid_edit_preserves_it(self):
        self.client.post('/drafts/new', data=self.data)
        self.assertEqual(self.client.get('/drafts/1/edit').status_code, 200)
        updated = self.data | dict(title='Updated garden', source_id='')
        self.assertEqual(self.client.post('/drafts/1/edit', data=updated).status_code, 302)
        self.assertEqual(self.client.post('/drafts/1/edit', data=updated | dict(title='')).status_code, 400)
        self.assertEqual(self.client.post('/drafts/1/edit', data=updated | dict(csrf_token='wrong')).status_code, 400)
        connection = database()
        try:
            records = connection.execute('SELECT * FROM drafts').fetchall()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]['title'], 'Updated garden')
            self.assertEqual(records[0]['source_id'], '')
        finally:
            connection.close()

    def test_delete_requires_confirmation_and_valid_token(self):
        self.client.post('/drafts/new', data=self.data)
        self.assertEqual(self.client.get('/drafts/1/delete').status_code, 200)
        self.assertEqual(self.client.get('/drafts/1').status_code, 200)
        for data in [dict(csrf_token=self.token), dict(csrf_token='bad', confirm='delete')]:
            self.assertEqual(self.client.post('/drafts/1/delete', data=data).status_code, 400)
            self.assertEqual(self.client.get('/drafts/1').status_code, 200)
        self.assertEqual(self.client.post('/drafts/1/delete', data=dict(csrf_token=self.token, confirm='delete')).status_code, 302)
        self.assertEqual(self.client.get('/drafts/1').status_code, 404)
        self.assertEqual(self.client.get('/drafts/1/edit').status_code, 404)
        self.assertEqual(self.client.get('/drafts/1/delete').status_code, 404)
        self.assertEqual(self.client.get('/projects/garden-mulch').status_code, 200)

    def test_accounts_isolate_all_draft_operations(self):
        self.client.post('/drafts/new', data=self.data)
        bob = app.test_client()
        bob.get('/register')
        with bob.session_transaction() as session:
            token = session['csrf_token']
        bob.post('/register', data=dict(csrf_token=token, username='bob', password='another-password-123', confirmation='another-password-123'))
        bob.post('/login', data=dict(csrf_token=token, username='bob', password='another-password-123'))
        bob.get('/drafts')
        with bob.session_transaction() as session:
            token = session['csrf_token']
        self.assertNotIn('&lt;script&gt;', bob.get('/drafts').get_data(as_text=True))
        for path in ['/drafts/1', '/drafts/1/edit', '/drafts/1/delete']:
            self.assertEqual(bob.get(path).status_code, 404)
        for suffix in ['edit', 'delete']:
            self.assertEqual(bob.post('/drafts/1/' + suffix, data=self.data | dict(csrf_token=token, confirm='delete')).status_code, 404)
        self.assertEqual(self.client.get('/drafts/1').status_code, 200)
        anonymous = app.test_client()
        self.assertEqual(anonymous.get('/drafts').status_code, 302)
        self.assertEqual(anonymous.post('/drafts/new', data=self.data).status_code, 302)

    def test_auth_validation_and_logout(self):
        connection = database()
        try:
            stored = connection.execute('SELECT password_hash FROM users').fetchone()[0]
            self.assertNotEqual(stored, 'long-password-123')
        finally:
            connection.close()
        self.assertEqual(self.client.post('/register', data=dict(csrf_token=self.token, username='ALICE', password='long-password-123', confirmation='long-password-123')).status_code, 400)
        self.assertEqual(self.client.post('/login', data=dict(csrf_token=self.token, username='alice', password='incorrect')).status_code, 400)
        self.assertEqual(self.client.get('/logout').status_code, 405)
        self.assertEqual(self.client.post('/logout', data=dict(csrf_token='bad')).status_code, 400)
        self.assertEqual(self.client.post('/logout', data=dict(csrf_token=self.token)).status_code, 302)
        self.assertEqual(self.client.get('/drafts').status_code, 302)

    def test_unowned_drafts_remain_hidden_until_explicit_assignment(self):
        connection = database()
        try:
            with connection:
                connection.execute("INSERT INTO drafts (title,country,problem,approach,conditions,source_id) VALUES ('Legacy record','Nigeria','Water','Monitor','','')")
        finally:
            connection.close()
        self.assertNotIn('Legacy record', self.client.get('/drafts').get_data(as_text=True))
        self.assertEqual(self.client.get('/drafts/1').status_code, 404)
        result = app.test_cli_runner().invoke(args=['assign-legacy-drafts', 'alice'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Legacy record', self.client.get('/drafts').get_data(as_text=True))

    def test_missing_draft(self):
        self.assertEqual(self.client.get('/drafts/999').status_code, 404)

    def test_progress_persistence_validation_status_and_deletion(self):
        self.client.post('/drafts/new', data=self.data)
        record = dict(csrf_token=self.token, entry_date='2026-01-01', observation='Initial reading', measurement='0', unit='litres', metric='Water used', period='One week', entry_type='baseline')
        self.assertEqual(self.client.post('/drafts/1/progress', data=record).status_code, 302)
        for changes in [dict(measurement='NaN'), dict(measurement='-1'), dict(unit=''), dict(entry_date='invalid'), dict(csrf_token='bad')]:
            self.assertEqual(self.client.post('/drafts/1/progress', data=record | changes).status_code, 400)
        notes = record | dict(measurement='', unit='', metric='', period='', entry_type='observation', observation='Notes only')
        self.assertEqual(self.client.post('/drafts/1/progress', data=notes).status_code, 302)
        self.assertIn('No measurement recorded.', self.client.get('/drafts/1/progress').get_data(as_text=True))
        self.assertEqual(self.client.post('/drafts/1/status', data=dict(csrf_token=self.token,status='ongoing')).status_code, 302)
        self.assertEqual(self.client.post('/drafts/1/status', data=dict(csrf_token=self.token,status='invalid')).status_code, 400)
        connection = database()
        try:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM progress_entries').fetchone()[0], 2)
            self.assertEqual(connection.execute('SELECT status FROM drafts').fetchone()[0], 'ongoing')
        finally:
            connection.close()
        other = app.test_client()
        with other.session_transaction() as session:
            session['user_id'] = 999
        self.assertEqual(other.get('/drafts/1/progress').status_code, 302)
        connection = database()
        try:
            with connection:
                connection.execute("INSERT INTO users (username,password_hash) VALUES ('bob','unused')")
            bob_id = connection.execute("SELECT id FROM users WHERE username='bob'").fetchone()[0]
        finally:
            connection.close()
        with other.session_transaction() as session:
            session['user_id'] = bob_id
            session['csrf_token'] = 'bob-token'
        self.assertEqual(other.get('/drafts/1/progress').status_code, 404)
        self.assertEqual(other.post('/drafts/1/progress', data=record | dict(csrf_token='bob-token')).status_code, 404)
        self.assertEqual(other.post('/drafts/1/status', data=dict(csrf_token='bob-token',status='completed')).status_code, 404)
        self.client.post('/drafts/1/delete', data=dict(csrf_token=self.token,confirm='delete'))
        connection = database()
        try:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM progress_entries').fetchone()[0], 0)
        finally:
            connection.close()


if __name__ == '__main__':
    unittest.main()
