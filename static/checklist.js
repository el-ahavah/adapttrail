(() => {
  'use strict';
  const page = document.querySelector('[data-checklist]');
  if (!page) return;
  const list = page.querySelector('[data-active-tasks]');
  const cards = [...list.querySelectorAll('[data-task-state]')];
  const tools = page.querySelector('[data-task-tools]');
  const status = page.querySelector('[data-task-results]');
  const search = page.querySelector('[data-task-search]');
  const sort = page.querySelector('[data-task-sort]');
  let filter = 'all';
  function updateView() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    cards.forEach(card => {
      const title = card.querySelector('h3').textContent.toLocaleLowerCase();
      card.hidden = (filter !== 'all' && card.dataset.taskState !== filter) || !terms.every(term => title.includes(term));
      if (!card.hidden) shown++;
    });
    const ordered = [...cards].sort((a, b) => {
      const byAge = Number(a.dataset.taskId) - Number(b.dataset.taskId);
      if (sort.value === 'newest') return -byAge;
      if (sort.value === 'todo') return Number(a.dataset.taskState === 'done') - Number(b.dataset.taskState === 'done') || byAge;
      return byAge;
    });
    ordered.forEach(card => list.appendChild(card));
    status.textContent = `${shown} of ${cards.length} active tasks shown.`;
    page.querySelector('[data-task-no-results]').hidden = shown > 0 || cards.length === 0;
  }
  sort.addEventListener('change', updateView);
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
  const composer = page.querySelector('[data-task-composer]');
  const title = composer.querySelector('textarea');
  const starters = page.querySelector('[data-task-starters]');
  function resizeTitle() { title.style.height = 'auto'; title.style.height = `${Math.min(260, title.scrollHeight)}px`; }
  function updateStarters() { starters.hidden = title.value.trim().length > 0; resizeTitle(); }
  starters.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
    title.value = button.textContent;
    title.dispatchEvent(new Event('input', { bubbles: true }));
    title.focus();
  }));
  title.addEventListener('input', updateStarters);
  title.addEventListener('keydown', event => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) { event.preventDefault(); composer.requestSubmit(); }
  });
  page.querySelector('[data-task-shortcut]').hidden = false;
  updateStarters();
  const ring = page.querySelector('[data-progress-ring]');
  const total = Number(ring.dataset.total);
  const percent = total ? Math.round(Number(ring.dataset.completed) / total * 100) : 0;
  if (total) {
    ring.hidden = false;
    ring.querySelector('[data-progress-percent]').textContent = `${percent}%`;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motion.matches) ring.style.setProperty('--completion', `${percent}%`);
    else {
      const start = performance.now();
      const animate = now => {
        const fraction = Math.min((now - start) / 650, 1);
        ring.style.setProperty('--completion', `${percent * (1 - (1 - fraction) ** 3)}%`);
        if (fraction < 1 && ring.isConnected && !motion.matches) requestAnimationFrame(animate);
        else ring.style.setProperty('--completion', `${percent}%`);
      };
      requestAnimationFrame(animate);
    }
  }
  updateView();
})();
