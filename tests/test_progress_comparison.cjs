const { test } = require('node:test');
const assert = require('node:assert/strict');
const { compareMeasurements: compare } = require('../static/progress-comparison.js');
const baseline = { kind: 'baseline', date: '2026-09-01', amount: '100', metric: 'Water used', unit: 'litres', period: '1–7 September' };
const followup = { ...baseline, kind: 'follow-up', date: '2026-10-01', amount: '75', period: '1–7 October' };
test('calculates increases, decreases and unchanged measurements', () => {
  assert.equal(compare(baseline, followup, true).difference, -25);
  assert.equal(compare(baseline, { ...followup, amount: '120' }, true).difference, 20);
  assert.equal(compare(baseline, { ...followup, amount: '100' }, true).difference, 0);
});
test('zero baseline is valid without division', () => assert.equal(compare({ ...baseline, amount: '0' }, followup, true).difference, 75));
test('missing, negative and nonfinite measurements cannot become zero', () => {
  for (const amount of ['', ' ', null, undefined, '-1', 'Infinity', 'NaN']) assert.ok(compare({ ...baseline, amount }, followup, true).error);
});
test('requires matching metrics and units without converting', () => {
  assert.ok(compare(baseline, { ...followup, unit: 'gallons' }, true).error);
  assert.ok(compare(baseline, { ...followup, metric: 'Rainfall' }, true).error);
  assert.equal(compare(baseline, { ...followup, metric: ' water USED ', unit: ' LITRES ' }, true).difference, -25);
});
test('requires correct entry types and chronological dates', () => {
  assert.ok(compare(followup, baseline, true).error);
  assert.ok(compare(baseline, { ...followup, date: '2026-08-01' }, true).error);
});
test('requires selections, periods and explicit comparability confirmation', () => {
  assert.ok(compare(null, followup, true).error);
  assert.ok(compare(baseline, followup, false).error);
  assert.ok(compare(baseline, { ...followup, period: '' }, true).error);
});
