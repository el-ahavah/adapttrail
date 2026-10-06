/* Apply the saved theme before styles load to avoid a bright flash. */
(() => {
  let saved;
  try { saved = localStorage.getItem('adapttrail-theme'); } catch (_) {}
  const theme = saved === 'light' || saved === 'dark' ? saved :
    (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.dataset.theme = theme;
})();
