import unittest
from app import app, database
from storage import IntegrityErrors
from test_drafts import DraftTests
from assessment import FIELDS


class SuggestedTaskTests(unittest.TestCase):
    setUp = DraftTests.setUp
    tearDown = DraftTests.tearDown

    def prepare(self):
        self.client.post('/drafts/new', data=self.data)
        answers = {key: 'unknown' for key in FIELDS}
        answers.update(csrf_token=self.token, approach='rainwater', country='Nigeria',region='',crop='',resources='')
        self.client.post('/drafts/1/assess', data=answers)
        return '/drafts/1/assessments/1/tasks/0'

    def test_preview_edit_save_source_and_duplicate_after_archive(self):
        path = self.prepare()
        self.assertIn(b'Add to my checklist', self.client.get('/assessments/1').data)
        self.assertEqual(self.client.get(path).status_code, 200)
        connection = database()
        self.assertEqual(connection.execute('SELECT COUNT(*) FROM project_tasks').fetchone()[0],0)
        connection.close()
        saved = self.client.post(path, data=dict(csrf_token=self.token,title='Ask our local adviser'))
        self.assertEqual(saved.status_code,302)
        page = self.client.get(saved.location).data
        self.assertIn(b'Ask our local adviser',page)
        self.assertIn(b'From saved assessment #1',page)
        self.assertIn(b'Already on your checklist',self.client.get(path).data)
        self.assertIn(b'View checklist task',self.client.get('/assessments/1').data)
        for intent in ['complete','archive']:
            self.client.post('/drafts/1/tasks/1',data=dict(csrf_token=self.token,intent=intent))
        repeated = self.client.post(path,data=dict(csrf_token=self.token,title='Must not overwrite'))
        self.assertIn('archived=1', repeated.location)
        connection = database()
        try:
            rows=connection.execute('SELECT * FROM project_tasks').fetchall()
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]['title'],'Ask our local adviser')
            self.assertEqual(rows[0]['completed'],1)
            self.assertEqual(rows[0]['archived'],1)
        finally: connection.close()

    def test_invalid_input_and_source_do_not_save(self):
        path=self.prepare()
        for data in [dict(title='x'),dict(csrf_token=self.token,title=' '),dict(csrf_token=self.token,title='x'*241)]:
            self.assertEqual(self.client.post(path,data=data).status_code,400)
        self.assertEqual(self.client.get(path[:-1]+'999').status_code,404)
        self.client.post('/drafts/new',data=self.data)
        self.assertEqual(self.client.get('/drafts/2/assessments/1/tasks/0').status_code,404)
        self.assertEqual(self.client.post('/drafts/2/assessments/1/tasks/0',data=dict(csrf_token=self.token,title='Wrong project')).status_code,404)
        connection=database()
        try:self.assertEqual(connection.execute('SELECT COUNT(*) FROM project_tasks').fetchone()[0],0)
        finally:connection.close()

    def test_other_account_cannot_read_or_import_guidance(self):
        path=self.prepare()
        other=app.test_client()
        self.assertEqual(other.get(path).status_code,302)
        other.get('/register')
        with other.session_transaction() as saved:token=saved['csrf_token']
        other.post('/register',data=dict(csrf_token=token,username='suggestion_bob',password='long-password-123',confirmation='long-password-123'))
        other.post('/login',data=dict(csrf_token=token,username='suggestion_bob',password='long-password-123'))
        other.get('/drafts')
        with other.session_transaction() as saved:token=saved['csrf_token']
        self.assertEqual(other.get(path).status_code,404)
        self.assertEqual(other.post(path,data=dict(csrf_token=token,title='Intrusion')).status_code,404)

    def test_source_is_server_controlled_and_title_is_escaped(self):
        path=self.prepare()
        saved=self.client.post(path,data=dict(csrf_token=self.token,title='<script>private task</script>',source_assessment_id=999,source_check_index=99))
        self.assertIn(b'&lt;script&gt;private task&lt;/script&gt;',self.client.get(saved.location).data)
        connection=database()
        try:
            row=connection.execute('SELECT * FROM project_tasks').fetchone()
            self.assertEqual(row['source_assessment_id'],1)
            self.assertEqual(row['source_check_index'],0)
            # A database constraint protects against simultaneous/replayed inserts too.
            with self.assertRaises(IntegrityErrors):
                connection.execute('INSERT INTO project_tasks(project_id,title,source_assessment_id,source_check_index) VALUES (1,?,1,0)',('Duplicate',))
            connection.rollback()
        finally:connection.close()

    def test_preview_login_return_path(self):
        from app import safe_return_path
        self.assertTrue(safe_return_path('/drafts/1/assessments/2/tasks/0'))
        self.assertFalse(safe_return_path('//evil.test/drafts/1/assessments/2/tasks/0'))
        self.assertFalse(safe_return_path('/drafts/1/assessments/2/tasks/0/extra'))


del DraftTests
