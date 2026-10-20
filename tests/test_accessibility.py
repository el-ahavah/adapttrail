"""Stage 5 public display preferences; no database or weather calls required."""
import unittest
from app import app


class DataModeTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.get('/accessibility')
        with self.client.session_transaction() as saved:
            self.token = saved['csrf_token']

    def choose(self, mode, **extra):
        return self.client.post('/accessibility', data={
            'csrf_token': self.token, 'data_mode': mode, **extra})

    def test_standard_and_low_data_asset_requests(self):
        normal = self.client.get('/')
        self.assertIn(b'/static/app.js', normal.data)
        self.assertIn(b'/static/landscape.svg', normal.data)
        saved = self.choose('low')
        self.assertEqual(saved.status_code, 303)
        self.assertIn('HttpOnly', saved.headers['Set-Cookie'])
        self.assertIn('SameSite=Lax', saved.headers['Set-Cookie'])
        home = self.client.get('/')
        self.assertNotIn(b'/static/app.js', home.data)
        self.assertNotIn(b'/static/landscape.svg', home.data)
        self.assertIn(b'/static/accessibility.js', home.data)
        self.assertIn(b'id="main-navigation"', home.data)
        self.assertIn(b'tabindex="-1"', home.data)
        self.assertIn(b'Low-data mode on', home.data)
        self.choose('standard')
        self.assertIn(b'/static/app.js', self.client.get('/').data)

    def test_explicit_choice_overrides_browser_hint(self):
        self.assertNotIn(b'/static/app.js',
                         self.client.get('/', headers={'Save-Data': 'on'}).data)
        self.choose('standard')
        self.assertIn(b'/static/app.js',
                      self.client.get('/', headers={'Save-Data': 'on'}).data)
        self.choose('low')
        self.assertNotIn(b'/static/app.js',
                         self.client.get('/', headers={'Save-Data': 'off'}).data)

    def test_rejected_post_does_not_change_preference(self):
        for data in ({'data_mode': 'low'},
                     {'data_mode': 'low', 'csrf_token': 'invalid'},
                     {'data_mode': 'unexpected', 'csrf_token': self.token}):
            response = self.client.post('/accessibility', data=data)
            self.assertEqual(response.status_code, 400)
            self.assertNotIn('adapttrail-data-mode=', response.headers.get('Set-Cookie', ''))
        self.assertIn(b'/static/app.js', self.client.get('/').data)

    def test_choice_survives_session_clear_and_does_not_leak_to_other_browser(self):
        self.choose('low')
        self.client.post('/logout', data={'csrf_token': self.token})
        self.assertNotIn(b'/static/app.js', self.client.get('/').data)
        self.assertIn(b'/static/app.js', app.test_client().get('/').data)

    def test_personalized_html_is_not_shared_cached(self):
        for path in ('/', '/accessibility', '/how-to-use'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            self.assertIn('Cookie', response.vary)
            self.assertIn('Save-Data', response.vary)
