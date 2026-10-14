import unittest
from app import app, database
from test_drafts import DraftTests


class TaskObservationTests(unittest.TestCase):
    setUp = DraftTests.setUp
    tearDown = DraftTests.tearDown

    def prepare(self):
        self.client.post('/drafts/new', data=self.data)
        self.client.post('/drafts/1/tasks',data=dict(csrf_token=self.token,title='Record the starting water use'))
        self.client.post('/drafts/1/tasks/1',data=dict(csrf_token=self.token,intent='complete'))
        return dict(csrf_token=self.token,source_task_id='1',entry_date='2026-01-01',entry_type='observation',observation='Measured the container; scale was hard to read.',measurement='',metric='',unit='',period='')

    def test_link_save_reopen_rename_archive_and_history(self):
        data=self.prepare()
        self.assertIn(b'Record what happened',self.client.get('/drafts/1/tasks').data)
        self.assertIn(b'Recording an observation for a completed task',self.client.get('/drafts/1/progress?task_id=1').data)
        self.assertEqual(self.client.post('/drafts/1/progress',data=data).status_code,302)
        self.assertIn(b'1 observation',self.client.get('/drafts/1/tasks').data)
        for intent in ['reopen','archive']:
            self.client.post('/drafts/1/tasks/1',data=dict(csrf_token=self.token,intent=intent))
        self.client.post('/drafts/1/tasks/1',data=dict(csrf_token=self.token,intent='edit',title='Renamed task'))
        for path in ['/drafts/1/progress','/drafts/1/history']:
            page=self.client.get(path).data
            self.assertIn(b'Record the starting water use',page)
            self.assertIn(b'View linked task',page)
            self.assertIn(b'Measured the container',page)
        self.assertIn(b'1 observation',self.client.get('/drafts/1/tasks').data)
        connection=database()
        try:
            row=connection.execute('SELECT * FROM progress_entries').fetchone()
            self.assertEqual(row['source_task_id'],1)
            self.assertEqual(row['source_task_title'],'Record the starting water use')
        finally:connection.close()

    def test_invalid_source_and_wrong_project_are_rejected(self):
        data=self.prepare()
        self.client.post('/drafts/new',data=self.data)
        for task_id, status in [('abc',400),('999',404),('-1',400)]:
            self.assertEqual(self.client.post('/drafts/1/progress',data=data|dict(source_task_id=task_id)).status_code,status)
        self.assertEqual(self.client.post('/drafts/2/progress',data=data).status_code,404)
        self.client.post('/drafts/1/tasks/1',data=dict(csrf_token=self.token,intent='reopen'))
        self.assertEqual(self.client.post('/drafts/1/progress',data=data).status_code,404)
        connection=database()
        try:self.assertEqual(connection.execute('SELECT COUNT(*) FROM progress_entries').fetchone()[0],0)
        finally:connection.close()

    def test_form_errors_retain_task_and_user_input(self):
        data=self.prepare()
        page=self.client.post('/drafts/1/progress',data=data|dict(entry_date='invalid')).data
        self.assertIn(b'name="source_task_id" value="1"',page)
        self.assertIn(b'Measured the container',page)
        self.assertIn(b'Record the starting water use',page)
        self.assertEqual(self.client.post('/drafts/1/progress',data=data|dict(csrf_token='bad')).status_code,400)

    def test_measurements_and_unrelated_entries_still_work(self):
        data=self.prepare()
        measured=data|dict(entry_type='baseline',measurement='0',metric='Water used',unit='litres',period='One week')
        self.assertEqual(self.client.post('/drafts/1/progress',data=measured).status_code,302)
        self.assertEqual(self.client.post('/drafts/1/progress',data=data|dict(source_task_id='')).status_code,302)
        connection=database()
        try:
            rows=connection.execute('SELECT * FROM progress_entries ORDER BY id').fetchall()
            self.assertEqual(rows[0]['measurement'],'0')
            self.assertIsNone(rows[1]['source_task_id'])
            self.assertEqual(rows[1]['source_task_title'],'')
        finally:connection.close()

    def test_other_account_cannot_read_or_attach_to_task(self):
        data=self.prepare()
        other=app.test_client();other.get('/register')
        with other.session_transaction() as saved:token=saved['csrf_token']
        other.post('/register',data=dict(csrf_token=token,username='observation_bob',password='long-password-123',confirmation='long-password-123'))
        other.post('/login',data=dict(csrf_token=token,username='observation_bob',password='long-password-123'))
        other.get('/drafts')
        with other.session_transaction() as saved:token=saved['csrf_token']
        self.assertEqual(other.get('/drafts/1/progress?task_id=1').status_code,404)
        self.assertEqual(other.post('/drafts/1/progress',data=data|dict(csrf_token=token)).status_code,404)
        other.post('/drafts/new',data=self.data|dict(csrf_token=token,title='Other owner project'))
        self.assertEqual(other.post('/drafts/2/progress',data=data|dict(csrf_token=token)).status_code,404)

    def test_snapshot_is_server_owned_escaped_and_not_published(self):
        data=self.prepare()
        self.client.post('/drafts/1/tasks/1',data=dict(csrf_token=self.token,intent='edit',title='<script>Private task</script>'))
        self.client.post('/drafts/1/progress',data=data|dict(source_task_title='Forged title'))
        for path in ['/drafts/1/progress','/drafts/1/history']:
            page=self.client.get(path).data
            self.assertIn(b'&lt;script&gt;Private task&lt;/script&gt;',page)
            self.assertNotIn(b'<script>Private task</script>',page)
            self.assertNotIn(b'Forged title',page)
        public=dict(csrf_token=self.token,title='Shared story',country='Nigeria',problem='Local challenge',action='Test action',outcome='',lessons='Test lessons',intent='publish',consent='yes')
        published=self.client.post('/drafts/1/publish',data=public)
        self.assertEqual(published.status_code,302)
        self.assertNotIn(b'Private task',app.test_client().get(published.location).data)
        self.client.post('/drafts/1/delete',data=dict(csrf_token=self.token,confirm='delete'))
        connection=database()
        try:self.assertEqual(connection.execute('SELECT COUNT(*) FROM progress_entries').fetchone()[0],0)
        finally:connection.close()


del DraftTests
