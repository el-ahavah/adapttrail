import unittest
from app import app, database
from test_drafts import DraftTests


class AdaptationTests(unittest.TestCase):
    setUp = DraftTests.setUp
    tearDown = DraftTests.tearDown

    def test_create_edit_publish_withdraw_delete_and_ownership(self):
        self.client.post('/drafts/new',data=self.data)
        public=dict(csrf_token=self.token,title='Community source',country='Nigeria',problem='Dry soil',
                    action='Try soil cover',outcome='Source outcome only',lessons='Source lessons only',intent='publish',consent='yes')
        self.client.post('/drafts/1/publish',data=public)
        bob=app.test_client()
        bob.get('/register')
        with bob.session_transaction() as session: token=session['csrf_token']
        bob.post('/register',data=dict(csrf_token=token,username='bob',password='another-password',confirmation='another-password'))
        bob.post('/login',data=dict(csrf_token=token,username='bob',password='another-password'))
        form=bob.get('/drafts/from-community/1')
        self.assertEqual(form.status_code,200)
        self.assertIn(b'Try soil cover',form.data)
        self.assertNotIn(b'Source outcome only',form.data)
        with bob.session_transaction() as session: token=session['csrf_token']
        data=dict(csrf_token=token,title='My local trial',country='Ghana',problem='Dry soil here',
                  approach='Cover a small trial bed',conditions='Private soil notes',changes='<script>use local leaves</script>',reason='Private resource constraint')
        for change in [dict(csrf_token='forged'),dict(reason=''),dict(changes='x'*3001)]:
            self.assertEqual(bob.post('/drafts/from-community/1',data=data|change).status_code,400)
        saved=bob.post('/drafts/from-community/1',data=data)
        self.assertEqual(saved.status_code,302)
        path=saved.location
        page=bob.get(path).get_data(as_text=True)
        self.assertIn('&lt;script&gt;use local leaves&lt;/script&gt;',page)
        self.assertIn('Community source',page)
        self.assertNotIn('Source outcome only',page)
        self.assertEqual(self.client.get(path).status_code,404)
        self.assertEqual(self.client.get(path+'/adaptation').status_code,404)
        self.assertEqual(app.test_client().get('/drafts/from-community/1').status_code,302)
        self.assertIn(b'Private resource constraint',bob.get(path+'/history').data)
        self.assertEqual(bob.post(path+'/adaptation',data=dict(csrf_token=token,changes='Revised private plan',reason='Local cost')).status_code,302)
        self.assertIn(b'Revised private plan',bob.get(path).data)
        bob.post(path+'/publish',data=public|dict(csrf_token=token,title='Public adaptation'))
        visitor=app.test_client()
        page=visitor.get('/community/2').get_data(as_text=True)
        self.assertIn('/community/1',page)
        self.assertNotIn('Revised private plan',page)
        self.assertNotIn('Private soil notes',page)
        self.client.post('/drafts/1/unpublish',data=dict(csrf_token=self.token))
        self.assertEqual(bob.get('/drafts/from-community/1').status_code,404)
        self.assertEqual(bob.post('/drafts/from-community/1',data=data).status_code,404)
        self.assertIn(b'no longer publicly available',bob.get(path).data)
        self.assertNotIn('/community/1',visitor.get('/community/2').get_data(as_text=True))
        self.client.post('/drafts/1/delete',data=dict(csrf_token=self.token,confirm='delete'))
        self.assertEqual(bob.get(path).status_code,200)
        connection=database()
        try:
            row=connection.execute('SELECT * FROM adaptations').fetchone()
            self.assertIsNone(row['publication_id'])
            self.assertEqual(row['source_title'],'Community source')
        finally: connection.close()
        bob.post(path+'/delete',data=dict(csrf_token=token,confirm='delete'))
        connection=database()
        try: self.assertEqual(connection.execute('SELECT COUNT(*) FROM adaptations').fetchone()[0],0)
        finally: connection.close()

    def test_moderated_source_cannot_be_adapted(self):
        self.client.post('/drafts/new',data=self.data)
        self.client.post('/drafts/1/publish',data=dict(csrf_token=self.token,title='Source',country='',problem='Problem',
            action='Action',outcome='',lessons='Lessons',intent='publish',consent='yes'))
        app.test_cli_runner().invoke(args=['moderate-story','1'])
        self.assertEqual(self.client.get('/drafts/from-community/1').status_code,404)
        self.assertEqual(self.client.post('/drafts/from-community/1',data=self.data).status_code,404)


del DraftTests
