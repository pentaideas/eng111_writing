/* Theme choice is local to this reader's browser. */
(() => {
  'use strict';
  const themes = ['molasses', 'lantern', 'north-end'];
  const key = 'eng111-marco-theme';
  let selected = 'molasses';
  try {
    const saved = localStorage.getItem(key);
    if (themes.includes(saved)) selected = saved;
  } catch (_) { /* Theme switching still works when storage is unavailable. */ }
  document.documentElement.dataset.storyTheme = selected;

  function initialize() {
    const select = document.getElementById('story-theme');
    if (!select) return;
    select.value = selected;
    select.closest('.story-theme-control').hidden = false;
    select.addEventListener('change', () => {
      if (!themes.includes(select.value)) return;
      selected = select.value;
      document.documentElement.dataset.storyTheme = selected;
      try { localStorage.setItem(key, selected); } catch (_) { /* Optional persistence. */ }
    });
  }
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  else initialize();
})();
