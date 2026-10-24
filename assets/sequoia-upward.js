/* The poem is a native scroll surface, opened at its foot. No gesture trap or scroll animation. */
(() => {
  'use strict';
  const root = document.documentElement;
  const pane = document.querySelector('.upward-scroll');
  const foundation = document.querySelector('.upward-foundation');
  const poem = document.querySelector('.sequoia-lines');
  const replay = document.querySelector('[data-read-again]');
  const palette = document.getElementById('upward-palette');
  if (!pane || !foundation || !poem || !replay || !palette) return;
  const palettes = {
    bark: { bg:'#d5c0a1', ink:'#4a3125', subtle:'#624635', panel:'#ead7bd', hover:'#cbb18f' },
    parchment: { bg:'#f5f4ef', ink:'#253028', subtle:'#5d6d5f', panel:'#e8ece5', hover:'#d9e1d5' },
    dusk: { bg:'#182a23', ink:'#e1e8d9', subtle:'#bbcbb7', panel:'#263c31', hover:'#345141' }
  };
  const storageKey = 'sequoia-color-scheme';
  const params = new URLSearchParams(location.search);
  let stored = '';
  try { stored = localStorage.getItem(storageKey) || ''; } catch (_) {}
  function setPalette(name, save = false) {
    if (!palettes[name]) return;
    for (const [key,value] of Object.entries(palettes[name])) root.style.setProperty('--page-'+key,value);
    root.style.colorScheme = name === 'dusk' ? 'dark' : 'light';
    palette.value = name;
    if (save) {
      try { localStorage.setItem(storageKey,name); } catch (_) {}
      const url = new URL(location.href);
      url.searchParams.set('theme',name);
      history.replaceState(null,'',url.pathname+url.search+url.hash);
    }
  }
  setPalette(palettes[params.get('theme')] ? params.get('theme') : palettes[stored] ? stored : 'bark');
  palette.addEventListener('change',() => setPalette(palette.value,true));
  let interacted = false;
  let previousEnd = 0;
  function measure() {
    const wasAtFoot = !interacted || pane.scrollTop >= previousEnd - 4;
    // The title gets its own space, separate from the scroll surface.
    foundation.style.height = 'auto';
    root.style.setProperty('--foundation-height',Math.ceil(foundation.getBoundingClientRect().height)+'px');
    foundation.style.height = '';
    previousEnd = pane.scrollHeight - pane.clientHeight;
    if (wasAtFoot) pane.scrollTop = previousEnd;
  }
  function markInteraction() { interacted = true; }
  pane.addEventListener('wheel',markInteraction,{passive:true});
  pane.addEventListener('touchstart',markInteraction,{passive:true});
  pane.addEventListener('pointerdown',markInteraction,{passive:true});
  function readAgain() {
    pane.scrollTo({top:pane.scrollHeight,behavior:'instant'});
    pane.focus({preventScroll:true});
  }
  replay.addEventListener('click',readAgain);
  // Native wheel, touch and focused keyboard scrolling need no interception.
  // Also support reading keys when a visitor has not tabbed into the pane yet.
  document.addEventListener('keydown',event => {
    if (event.target !== document.body) return;
    const distance = event.key === 'ArrowUp' ? -60 : event.key === 'ArrowDown' ? 60 :
      event.key === 'PageUp' ? -pane.clientHeight*.8 : event.key === 'PageDown' ? pane.clientHeight*.8 : null;
    if (distance === null && !['Home','End'].includes(event.key)) return;
    interacted = true;
    event.preventDefault();
    if (distance !== null) pane.scrollBy({top:distance,behavior:'instant'});
    else pane.scrollTo({top:event.key === 'Home' ? 0 : pane.scrollHeight,behavior:'instant'});
  });
  pane.addEventListener('keydown',markInteraction);
  root.classList.add('upward-ready');
  measure();
  new ResizeObserver(measure).observe(poem);
  addEventListener('resize',measure,{passive:true});
  if (document.fonts) document.fonts.ready.then(measure);
  replay.hidden = false;
})();
