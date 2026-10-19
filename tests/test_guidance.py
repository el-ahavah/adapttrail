import json
import unittest
from unittest.mock import patch
from assessment import FIELDS, assess
from guidance import add_guidance
from app import app, database
from test_drafts import DraftTests


def answers(**changes):
    return {key: 'unknown' for key in FIELDS} | dict(crop='', resources='') | changes


def generate(approach='garden-mulch', weather=None, **changes):
    values = answers(**changes)
    result = assess(approach, values)
    if weather:
        result['weather'] = weather
    return add_guidance(approach, values, result)


class GuidanceRulesTests(unittest.TestCase):
    def test_maize_stage_is_explicit_not_inferred(self):
        for crop in ['maize', ' CORN ', 'Grain   Maize']:
            result = generate(crop=crop, growth='flowering', water='low')
            cards = result['guidance']['cards']
            self.assertTrue(result['guidance']['maize'])
            self.assertIn('maize-sensitive-stage', [c['rule'] for c in cards])
            self.assertTrue(next(c for c in cards if c['rule']=='maize-sensitive-stage')['source']['url'].startswith('https://www.fao.org/'))
        for stage in ['established', 'unknown', 'seedling', 'vegetative', 'ripening', 'not applicable']:
            ids = [c['rule'] for c in generate(crop='maize', growth=stage)['guidance']['cards']]
            self.assertNotIn('maize-sensitive-stage', ids)
            self.assertIn('maize-stage-check', ids)

    def test_unsupported_crops_and_approaches_are_not_classified(self):
        for crop in ['', 'tomato', 'maize and beans', 'cornflower', '<script>maize</script>']:
            guidance = generate(crop=crop)['guidance']
            self.assertFalse(guidance['maize'])
            self.assertTrue(any('Crop-specific guidance is unavailable' in gap for gap in guidance['gaps']))
        for approach in ['rainwater', 'water-log']:
            self.assertFalse(generate(approach, crop='maize', growth='flowering')['guidance']['maize'])

    def test_constraints_precede_general_steps_without_water_prescription(self):
        cards = generate(soil='sandy', drainage='poor', water='low', budget='low', maintenance='unavailable')['guidance']['cards']
        self.assertEqual(cards[0]['rule'], 'drainage-first')
        self.assertEqual(cards[1]['rule'], 'upkeep-plan')
        self.assertIn('does not mean this soil needs more water', cards[0]['why'])
        self.assertIn('limited-water', [c['rule'] for c in cards])
        self.assertIn('budget-plan', [c['rule'] for c in cards])
        self.assertNotIn('sandy-observation', [c['rule'] for c in generate()['guidance']['cards']])

    def test_weather_optional_no_drought_or_forecast_inference(self):
        snapshot = dict(location=dict(label='Test town'), retrieved_at='2026-10-19T12:00:00Z',
                        days=[dict(date=f'2026-10-{i}',precipitation=0) for i in range(18,22)])
        self.assertNotIn('weather-context', [c['rule'] for c in generate()['guidance']['cards']])
        result = generate(weather=snapshot)
        card = next(c for c in result['guidance']['cards'] if c['rule']=='weather-context')
        self.assertIn('do not establish drought', card['action'])
        snapshot['days'][2]['precipitation'] = 4
        wet = generate(weather=snapshot)
        self.assertIn('even when rain is forecast', next(c for c in wet['guidance']['cards'] if c['rule']=='weather-context')['action'])
        self.assertEqual(card['weather_basis']['dates'], ['2026-10-19','2026-10-20','2026-10-21'])

    def test_all_suggestions_have_valid_check_indices_and_bounded_actions(self):
        for approach in ['garden-mulch','rainwater','water-log']:
            result = generate(approach, crop='maize',soil='clay',growth='grain filling',water='low',budget='low',maintenance='unavailable',use='food crops')
            base = assess(approach, answers(crop='maize',soil='clay',growth='grain filling',water='low',budget='low',maintenance='unavailable',use='food crops'))
            self.assertEqual(result['checks'][:len(base['checks'])],base['checks'])
            for card in result['guidance']['cards']:
                self.assertEqual(result['checks'][card['check_index']], card['action'])
                self.assertLessEqual(len(card['action']),240)
                self.assertTrue(card['why'])
        self.assertIn('rainwater-quality', [c['rule'] for c in generate('rainwater',use='food crops')['guidance']['cards']])


class GuidanceFlowTests(unittest.TestCase):
    setUp = DraftTests.setUp
    tearDown = DraftTests.tearDown

    def test_saved_guidance_to_task_to_observation(self):
        self.client.post('/drafts/new',data=self.data)
        values = answers(crop='maize',growth='flowering',soil='sandy',water='low',approach='garden-mulch',csrf_token=self.token)
        saved = self.client.post('/drafts/1/assess',data=values)
        self.assertEqual(saved.status_code,302)
        self.assertIn(b'Suggested next steps for your conditions',self.client.get(saved.location).data)
        connection = database()
        try:
            row = connection.execute('SELECT * FROM assessments WHERE id=1').fetchone()
            result = json.loads(row['result'])
            self.assertEqual(row['rule_version'],'preliminary-3-explained')
        finally: connection.close()
        card = next(c for c in result['guidance']['cards'] if c['rule']=='maize-sensitive-stage')
        task_path = '/drafts/1/assessments/1/tasks/' + str(card['check_index'])
        for _ in range(2):
            self.assertEqual(self.client.post(task_path,data=dict(csrf_token=self.token,title=card['action'])).status_code,302)
        self.client.post('/drafts/1/tasks/1',data=dict(csrf_token=self.token,intent='complete'))
        observation = dict(csrf_token=self.token,source_task_id='1',entry_date='2026-01-01',entry_type='observation',observation='Asked local adviser; checking crop stage next.')
        self.assertEqual(self.client.post('/drafts/1/progress',data=observation).status_code,302)
        self.assertIn(b'Asked local adviser',self.client.get('/drafts/1/history').data)
        with patch('guidance.SOURCES', {}):
            self.assertIn(b'FAO: Water shortages',self.client.get(saved.location).data)
        self.assertEqual(app.test_client().get(saved.location).status_code,302)

    def test_legacy_snapshot_remains_readable_and_not_recomputed(self):
        self.client.post('/drafts/new',data=self.data)
        result = assess('garden-mulch', answers())
        connection = database()
        try:
            with connection:
                connection.execute('INSERT INTO assessments(user_id,project_id,approach,inputs,result,rule_version) VALUES (1,1,?,?,?,?)',
                                   ('garden-mulch', json.dumps(answers()), json.dumps(result),'preliminary-2-weather'))
        finally: connection.close()
        page = self.client.get('/assessments/1')
        self.assertEqual(page.status_code,200)
        self.assertNotIn(b'Suggested next steps for your conditions',page.data)
        self.assertIn(b'preliminary-2-weather',page.data)

    def test_weather_failure_still_saves_explained_guidance(self):
        from weather import WeatherUnavailable
        self.client.post('/drafts/new',data=self.data)
        with self.client.session_transaction() as session:
            session['weather_locations']=[dict(id='1', label='Town', latitude=0,longitude=0)]
        with patch('app.forecast',side_effect=WeatherUnavailable('Weather service unavailable.')):
            saved=self.client.post('/drafts/1/assess',data=answers(csrf_token=self.token,approach='garden-mulch',crop='maize',growth='flowering',weather_location='1'))
        self.assertEqual(saved.status_code,302)
        self.assertIn(b'No weather snapshot: no weather-based suggestion',self.client.get(saved.location).data)


del DraftTests
