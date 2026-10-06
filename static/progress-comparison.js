(function () {
  'use strict';
  const normalise = value => String(value || '').trim().toLocaleLowerCase();
  function compareMeasurements(baseline, followup, confirmed) {
    if (!baseline || !followup) return { error: 'Choose a baseline and a follow-up measurement. If none are listed, save entries of those types first.' };
    if (baseline.kind !== 'baseline' || followup.kind !== 'follow-up') return { error: 'Choose a baseline and a follow-up entry.' };
    if (!normalise(baseline.metric) || !normalise(baseline.unit) || normalise(baseline.metric) !== normalise(followup.metric) || normalise(baseline.unit) !== normalise(followup.unit)) return { error: 'These metrics or units do not match. Choose matching measurements; no unit conversion is applied.' };
    if (!baseline.date || !followup.date || followup.date < baseline.date) return { error: 'The follow-up observation date must be on or after the baseline date.' };
    const amounts = [baseline.amount, followup.amount];
    if (amounts.some(value => value === null || value === undefined || String(value).trim() === '' || !Number.isFinite(Number(value)) || Number(value) < 0)) return { error: 'Both entries need valid recorded measurements. Missing values are not zero.' };
    if (!normalise(baseline.period) || !normalise(followup.period) || !confirmed) return { error: 'Check the displayed measurement periods, methods and scope, then confirm that they are comparable.' };
    return { difference: Number(followup.amount) - Number(baseline.amount), metric: baseline.metric, unit: baseline.unit };
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = { compareMeasurements };
  if (typeof document === 'undefined') return;
  const panel = document.querySelector('[data-progress-comparison]');
  if (!panel) return;
  const baseline = panel.querySelector('[data-compare-baseline]');
  const followup = panel.querySelector('[data-compare-followup]');
  const confirmed = panel.querySelector('[data-compare-confirm]');
  const result = panel.querySelector('[data-compare-result]');
  const selected = select => select.value ? select.selectedOptions[0].dataset : null;
  function update() {
    const comparison = compareMeasurements(selected(baseline), selected(followup), confirmed.checked);
    if (comparison.error) { result.textContent = comparison.error; return; }
    const value = Math.abs(comparison.difference).toLocaleString(undefined, { maximumSignificantDigits: 12 });
    result.textContent = comparison.difference === 0
      ? `${comparison.metric}: no recorded difference (0 ${comparison.unit}) between these entries.`
      : `${comparison.metric}: the follow-up records ${value} ${comparison.unit} ${comparison.difference > 0 ? 'more' : 'less'} than the baseline.`;
  }
  [baseline, followup].forEach(select => select.addEventListener('change', () => { confirmed.checked = false; update(); }));
  confirmed.addEventListener('change', update);
  panel.hidden = false;
  update();
})();
