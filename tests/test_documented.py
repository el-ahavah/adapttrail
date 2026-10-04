import unittest
from app import app, database
from documented_projects import DOCUMENTED_PROJECTS
from test_drafts import DraftTests


class DocumentedTests(unittest.TestCase):
    setUp=DraftTests.setUp
    tearDown=DraftTests.tearDown

    def test_collection_provenance_filters_and_assessment_boundaries(self):
        self.assertEqual(len(DOCUMENTED_PROJECTS),6)
        self.assertEqual(len({p['id'] for p in DOCUMENTED_PROJECTS}),6)
        for project in DOCUMENTED_PROJECTS:
            page=self.client.get('/projects/'+project['id'])
            self.assertEqual(page.status_code,200)
            for value in ['Documented external project',project['source_url'],project['source_date'],'Evidence limitations','Local checks suggested by AdaptTrail']:
                self.assertIn(value,page.get_data(as_text=True))
            self.assertEqual(self.client.get('/assess/'+project['id']).status_code,404)
        page=self.client.get('/discover?action=Urban+heat+adaptation').get_data(as_text=True)
        self.assertIn('Cool roofs within Ahmedabad',page)
        self.assertNotIn('Restoring land in Tahoua',page)
        self.assertEqual(self.client.get('/drafts/from-documented/missing').status_code,404)
        self.assertEqual(app.test_client().get('/drafts/from-documented/niger-tahoua').status_code,302)

    def test_documented_adaptation_preserves_source_and_private_notes(self):
        data=dict(csrf_token=self.token,title='My land trial',country='Nigeria',problem='Local degradation',
                  approach='Plan a locally reviewed trial',conditions='Private condition',changes='Private planned change',reason='Private reason')
        self.assertEqual(self.client.post('/drafts/from-documented/niger-tahoua',data=data|dict(reason='')).status_code,400)
        saved=self.client.post('/drafts/from-documented/niger-tahoua',data=data|dict(source_id='india-cool-roofs'))
        self.assertEqual(saved.status_code,302)
        page=self.client.get(saved.location).get_data(as_text=True)
        self.assertIn('/projects/niger-tahoua',page)
        self.assertIn('Private planned change',page)
        self.assertEqual(self.client.get(saved.location+'/assess').status_code,200)
        edit=data|dict(source_id='rainwater')
        self.assertEqual(self.client.post(saved.location+'/edit',data=edit).status_code,302)
        connection=database()
        try: self.assertEqual(connection.execute('SELECT source_id FROM drafts').fetchone()['source_id'],'niger-tahoua')
        finally: connection.close()
        public=dict(csrf_token=self.token,title='My published trial',country='Nigeria',problem='Local degradation',action='Trial action',
                    outcome='Not measured yet',lessons='Public learning',intent='publish',consent='yes')
        published=self.client.post(saved.location+'/publish',data=public)
        page=app.test_client().get(published.location).get_data(as_text=True)
        self.assertIn('/projects/niger-tahoua',page)
        self.assertNotIn('Private planned change',page)
        self.assertNotIn('Private reason',page)
        self.assertNotIn('Private condition',page)
        self.client.post(saved.location+'/delete',data=dict(csrf_token=self.token,confirm='delete'))
        self.assertEqual(self.client.get('/projects/niger-tahoua').status_code,200)


del DraftTests
