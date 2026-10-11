(() => {
  'use strict';
  const page = document.querySelector('[data-checklist]');
  if (!page) return;
  const list = page.querySelector('[data-active-tasks]');
  const cards = [...list.querySelectorAll('[data-task-state]')];
  const tools = page.querySelector('[data-task-tools]');
  const status = page.querySelector('[data-task-results]');
  const search = page.querySelector('[data-task-search]');
  let filter = 'all';
  function updateView() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    cards.forEach(card => {
      const title = card.querySelector('h3').textContent.toLocaleLowerCase();
      card.hidden = (filter !== 'all' && card.dataset.taskState !== filter) || !terms.every(term => title.includes(term));
      if (!card.hidden) shown++;
    });
    status.textContent = `${shown} of ${cards.length} active tasks shown.`;
    page.querySelector('[data-task-no-results]').hidden = shown > 0 || cards.length === 0;
  }
  search.addEventListener('input', updateView);
  page.querySelector('[data-task-clear]').addEventListener('click', () => { search.value = ''; updateView(); search.focus(); });
  tools.hidden = cards.length === 0;
  tools.querySelectorAll('[data-task-filter]').forEach(button => {
    button.addEventListener('click', () => {
      filter = button.dataset.taskFilter;
      tools.querySelectorAll('[data-task-filter]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      updateView();
    });
  });
  updateView();
})();
