/* Essential feedback; no network requests or saved form values. */
(() => {
  const error = document.querySelector('main [role="alert"]');
  if (error) {
    error.setAttribute('tabindex', '-1');
    error.focus();
  }
})();
