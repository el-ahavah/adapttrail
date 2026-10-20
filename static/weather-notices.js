/* Progressive feedback only; native POST forms also work without JavaScript. */
(function () {
  'use strict';
  const forms = document.querySelectorAll('[data-weather-request]');
  forms.forEach(form => {
    form.addEventListener('submit', event => {
      if (form.dataset.sending === 'yes') { event.preventDefault(); return; }
      form.dataset.sending = 'yes';
      form.setAttribute('aria-busy', 'true');
      const feedback = form.querySelector('[data-weather-feedback]');
      if (feedback) feedback.textContent = event.submitter && event.submitter.value === 'refresh'
        ? 'Checking the forecast…' : 'Please wait…';
      // Keep the submitter enabled so the server receives its intent.
    });
  });
  window.addEventListener('pageshow', () => forms.forEach(form => {
    delete form.dataset.sending;
    form.removeAttribute('aria-busy');
    const feedback = form.querySelector('[data-weather-feedback]');
    if (feedback) feedback.textContent = '';
  }));
})();
