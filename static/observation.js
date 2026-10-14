(() => {
  'use strict';
  const form = document.querySelector('[data-observation-form]');
  if (!form) return;
  const field = form.querySelector('#observation');
  const button = form.querySelector('button');
  field.addEventListener('input', () => field.setCustomValidity(''));
  form.addEventListener('submit', event => {
    if (!field.value.trim()) { event.preventDefault(); field.setCustomValidity('Write an observation before saving.'); field.reportValidity(); return; }
    if (form.getAttribute('aria-busy') === 'true') { event.preventDefault(); return; }
    form.setAttribute('aria-busy', 'true'); button.textContent = 'Saving observation…';
  });
  window.addEventListener('pageshow', () => { form.removeAttribute('aria-busy'); button.textContent = 'Save progress entry'; });
})();
