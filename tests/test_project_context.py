import json
import sqlite3
import unittest
from app import app, database
from assessment import FIELDS
from storage import connect
from test_drafts import DraftTests


class ProjectContextTests(unittest.TestCase):
    setUp = DraftTests.setUp
    tearDown = DraftTests.tearDown

    def prepare(self):
        self.client.post('/drafts/new', data=self.data)
        return dict({key: 'unknown' for key in FIELDS}, csrf_token=self.token,
                    crop='Private maize', soil='loam', growth='seedling', region='General area', resources='Local materials')

    def stored(self):
        connection = database()
        try:
            return json.loads(connection.execute('SELECT farm_context FROM drafts WHERE id=1').fetchone()['farm_context'])
        finally:
            connection.close()

    def test_reuse_override_and_old_snapshot_preserved(self):
        data = self.prepare()
        self.assertEqual(self.client.post('/drafts/1/context', data=data).status_code, 302)
        self.assertEqual(self.stored()['crop'], 'Private maize')
        self.assertIn('updated_at', self.stored())
        self.assertIn(b'value="Private maize"', self.client.get('/drafts/1/assess').data)
        answers = data | dict(approach='garden-mulch', country='Nigeria', crop='Assessment only')
        saved = self.client.post('/drafts/1/assess', data=answers)
        self.assertEqual(saved.status_code, 302)
        self.assertEqual(self.stored()['crop'], 'Private maize')
        self.client.post('/drafts/1/context', data=data | dict(crop='New crop', growth='established'))
        self.assertIn(b'Assessment only', self.client.get(saved.location).data)
        self.assertNotIn(b'New crop', self.client.get(saved.location).data)
        self.assertIn(b'value="New crop"', self.client.get('/drafts/1/assess').data)
        self.assertNotIn(b'New crop', self.client.get('/assess/garden-mulch').data)
        self.client.post('/drafts/new', data=self.data)
        self.assertNotIn(b'New crop', self.client.get('/drafts/2/assess').data)

    def test_validation_csrf_unknowns_and_clear(self):
        data = self.prepare()
        self.client.post('/drafts/1/context', data=data)
        before = self.stored()
        for change in [dict(soil='forged'), dict(crop='x'*301), dict(csrf_token='bad')]:
            self.assertEqual(self.client.post('/drafts/1/context', data=data | change).status_code, 400)
            self.assertEqual(before, self.stored())
        response = self.client.post('/drafts/1/context', data=data | dict(soil='forged'))
        self.assertIn(b'value="Private maize"', response.data)
        cleared = {key: 'unknown' for key in FIELDS}
        self.assertEqual(self.client.post('/drafts/1/context', data=cleared | dict(csrf_token=self.token)).status_code, 302)
        self.assertEqual(self.stored()['crop'], '')
        self.assertEqual(self.stored()['soil'], 'unknown')

    def test_ownership_escaping_and_publication_privacy(self):
        data = self.prepare() | dict(crop='<script>private crop</script>')
        self.client.post('/drafts/1/context', data=data)
        self.assertIn(b'&lt;script&gt;private crop&lt;/script&gt;', self.client.get('/drafts/1/context').data)
        visitor = app.test_client()
        self.assertEqual(visitor.get('/drafts/1/context').status_code, 302)
        visitor.get('/register')
        with visitor.session_transaction() as saved: token = saved['csrf_token']
        visitor.post('/register', data=dict(csrf_token=token, username='bobcontext', password='long-password-123', confirmation='long-password-123'))
        visitor.post('/login', data=dict(csrf_token=token, username='bobcontext', password='long-password-123'))
        visitor.get('/drafts')
        with visitor.session_transaction() as saved: token = saved['csrf_token']
        self.assertEqual(visitor.get('/drafts/1/context').status_code, 404)
        self.assertEqual(visitor.post('/drafts/1/context', data=data | dict(csrf_token=token)).status_code, 404)
        public = dict(csrf_token=self.token,title='Shared story',country='Nigeria',problem='Challenge',action='Action',outcome='',lessons='Lessons',intent='publish',consent='yes')
        result = self.client.post('/drafts/1/publish', data=public)
        self.assertEqual(result.status_code, 302)
        self.assertNotIn(b'private crop', app.test_client().get(result.location).data)
        self.client.post('/drafts/1/delete', data=dict(csrf_token=self.token, confirm='delete'))
        self.assertEqual(self.client.get('/drafts/1/context').status_code, 404)

    def test_weather_search_and_errors_keep_assessment_edits(self):
        from unittest.mock import patch
        data = self.prepare()
        self.client.post('/drafts/1/context', data=data)
        answers = data | dict(approach='garden-mulch', crop='Temporary crop', weather_query='Town', intent='search_weather')
        with patch('app.search_locations', return_value=[]):
            page = self.client.post('/drafts/1/assess', data=answers)
        self.assertEqual(page.status_code, 400)
        self.assertIn(b'value="Temporary crop"', page.data)
        self.assertEqual(self.stored()['crop'], 'Private maize')
        self.assertNotIn('weather_location', self.stored())

    def test_local_upgrade_preserves_existing_project(self):
        self.prepare()
        connection = sqlite3.connect(app.config['DATABASE'])
        connection.execute('ALTER TABLE drafts DROP COLUMN farm_context')
        connection.commit(); connection.close()
        connection = connect(app.config)
        try:
            row = connection.execute('SELECT * FROM drafts WHERE id=1').fetchone()
            self.assertEqual(row['country'], 'Nigeria')
            self.assertEqual(row['farm_context'], '{}')
        finally:
            connection.close()


del DraftTests
