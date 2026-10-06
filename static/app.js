/* Progressive enhancements. Account and project forms remain server controlled. */
(() => {
  document.body.classList.add('js-ready');
  const themeButton = document.querySelector('[data-theme-toggle]');
  if (themeButton) {
    const updateThemeButton = () => {
      const dark = document.documentElement.dataset.theme === 'dark';
      const label = dark ? 'Switch to light mode' : 'Switch to dark mode';
      themeButton.setAttribute('aria-label', label);
      themeButton.title = label;
      themeButton.setAttribute('aria-pressed', String(dark));
      themeButton.querySelector('span').textContent = dark ? '☀' : '☾';
    };
    themeButton.hidden = false;
    updateThemeButton();
    themeButton.addEventListener('click', () => {
      const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = theme;
      try { localStorage.setItem('adapttrail-theme', theme); } catch (_) { /* Toggle still works without storage. */ }
      updateThemeButton();
    });
  }
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('[data-nav-toggle]');
  if (header && toggle) {
    toggle.hidden = false;
    const close = () => {
      header.dataset.menuOpen = 'false';
      toggle.setAttribute('aria-expanded', 'false');
      toggle.textContent = 'Menu ☰';
    };
    close();
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      header.dataset.menuOpen = String(open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.textContent = open ? 'Close ×' : 'Menu ☰';
    });
    header.addEventListener('keydown', event => {
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        close();
        toggle.focus();
      }
    });
  }
  const search = document.querySelector('[data-project-search]');
  if (search) {
    document.querySelector('[data-search-panel]').hidden = false;
    const groups = [...document.querySelectorAll('[data-search-group]')];
    const status = document.querySelector('[data-search-status]');
    const update = () => {
      const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0;
      for (const group of groups) {
        const cards = [...group.querySelectorAll('.card')];
        let matches = 0;
        for (const card of cards) {
          const text = card.textContent.toLocaleLowerCase();
          card.hidden = !terms.every(term => text.includes(term));
          if (!card.hidden) matches++;
        }
        const empty = group.querySelector('[data-search-empty]');
        if (empty) empty.hidden = matches > 0 || terms.length === 0 || cards.length === 0;
        visible += matches;
      }
      status.textContent = terms.length ? `${visible} matching project${visible === 1 ? '' : 's'} in the current action filter.` : 'Search the documented and community projects shown below.';
    };
    search.addEventListener('input', update);
    document.querySelector('[data-clear-search]').addEventListener('click', () => {
      search.value = '';
      update();
      search.focus();
    });
    update();
  }
  document.querySelectorAll('textarea[maxlength]').forEach(field => {
    const count = document.createElement('span');
    count.className = 'field-count';
    const update = () => { count.textContent = `${field.value.length} / ${field.maxLength} characters`; };
    field.insertAdjacentElement('afterend', count);
    field.addEventListener('input', update);
    update();
  });
})();
