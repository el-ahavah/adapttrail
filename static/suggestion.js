(() => {
  'use strict';
  const form = document.querySelector('.suggestion-form');
  if (!form) return;
  const title = form.querySelector('textarea');
  title.addEventListener('input', () => title.setCustomValidity(''));
  form.addEventListener('submit', event => {
    if (!title.value.trim()) { event.preventDefault(); title.setCustomValidity('Write a task before adding it.'); title.reportValidity(); return; }
    if (form.getAttribute('aria-busy') === 'true') { event.preventDefault(); return; }
    form.setAttribute('aria-busy', 'true');
    form.querySelector('button').textContent = 'Adding…';
  });
  window.addEventListener('pageshow', () => { form.removeAttribute('aria-busy'); form.querySelector('button').textContent = 'Add to my checklist'; });
})();
