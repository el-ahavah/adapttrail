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

    def test_missing_draft(self):
        self.assertEqual(self.client.get('/drafts/999').status_code, 404)


if __name__ == '__main__':
    unittest.main()
