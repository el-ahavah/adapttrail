import unittest
from app import app, database
from test_drafts import DraftTests


class JourneyTests(unittest.TestCase):
    setUp=DraftTests.setUp
    tearDown=DraftTests.tearDown

    def test_register_login_returns_to_selected_adaptation(self):
        visitor=app.test_client()
        target='/drafts/from-documented/niger-tahoua'
        self.assertEqual(visitor.get(target).status_code,302)
        visitor.get('/register')
        with visitor.session_transaction() as session: token=session['csrf_token']
        visitor.post('/register',data=dict(csrf_token=token,username='pilot_user',password='test-password',confirmation='test-password'))
        response=visitor.post('/login',data=dict(csrf_token=token,username='pilot_user',password='test-password'))
        self.assertEqual(response.location,target)
        self.assertEqual(visitor.get(target).status_code,200)
        with visitor.session_transaction() as session: self.assertNotIn('return_after_login',session)

    def test_return_destination_rejects_external_and_action_paths(self):
        for target in ['https://example.com','//example.com','/logout','/drafts/1/status','/drafts/1\nLocation: https://example.com']:
            visitor=app.test_client()
            visitor.get('/login')
            with visitor.session_transaction() as session:
                token=session['csrf_token']
                session['return_after_login']=target
            response=visitor.post('/login',data=dict(csrf_token=token,username='alice',password='long-password-123'))
            self.assertEqual(response.location,'/drafts')

    def test_external_project_requires_explicit_supported_assessment(self):
        data=dict(csrf_token=self.token,title='Pilot trial',country='Nigeria',problem='Local problem',approach='Locally reviewed action',
                  conditions='',changes='Trial change',reason='Local context')
        saved=self.client.post('/drafts/from-documented/india-cool-roofs',data=data)
        path=saved.location+'/assess'
        page=self.client.get(path).get_data(as_text=True)
        self.assertIn('Choose a supported approach',page)
        self.assertIn('do not assess an entire external or community project',page)
        self.assertNotIn('value="water-log" selected',page)
        from assessment import FIELDS
        answers={key:'unknown' for key in FIELDS}
        answers.update(csrf_token=self.token,country='',region='',crop='',resources='')
        self.assertEqual(self.client.post(path,data=answers|dict(approach='')).status_code,400)
        connection=database()
        try: self.assertEqual(connection.execute('SELECT COUNT(*) FROM assessments').fetchone()[0],0)
        finally: connection.close()
        self.assertEqual(self.client.post(path,data=answers|dict(approach='water-log')).status_code,302)
        help_page=app.test_client().get('/how-to-use')
        self.assertEqual(help_page.status_code,200)
        self.assertIn(b'does not collect or send feedback',help_page.data)


del DraftTests
