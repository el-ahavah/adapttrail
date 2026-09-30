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
        page = app.test_client().get(response.location).get_data(as_text=True)
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

    def test_missing_draft(self):
        self.assertEqual(self.client.get('/drafts/999').status_code, 404)


if __name__ == '__main__':
    unittest.main()
