/* Two scroll readings of the same Markdown story. No timers or forced scrolling. */
(() => {
  'use strict';
  const body = document.body;
  const article = document.querySelector('[data-story-source]');
  const toggle = document.querySelector('.marco-toggle');
  if (!article || !toggle) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const supportsFlood = CSS.supports('backdrop-filter', 'invert(1)') ||
    CSS.supports('-webkit-backdrop-filter', 'invert(1)');
  // Browsers without backdrop filters still get the fading-light experiment.
  const effect = body.dataset.effect === 'rise' && supportsFlood ? 'rise' : 'fade';
  body.dataset.effect = effect;
  let enabled = !reduced.matches;
  let pending = false;
  const light = [242, 229, 208];
  const dark = [24, 15, 11];
  const darkInk = [0, 0, 0];
  const lightInk = [255, 255, 255];
  const rgb = value => `rgb(${value.join(',')})`;
  const luminance = value => value.map(x => {
    x /= 255;
    return x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4;
  }).reduce((sum, x, i) => sum + x * [.2126, .7152, .0722][i], 0);
  const contrast = (a, b) => (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
  function update() {
    pending = false;
    const rect = article.getBoundingClientRect();
    // Start at the opening paragraph; reach full darkness when the final line is in view.
    const start = rect.top + scrollY - innerHeight * .22;
    const end = rect.bottom + scrollY - innerHeight * .8;
    const progress = enabled ? Math.max(0, Math.min(1, (scrollY - start) / Math.max(1, end - start))) : 0;
    body.dataset.effectEnabled = String(enabled);
    body.style.setProperty('--flood-top', `${100 * (1 - progress)}%`);
    const paper = effect === 'fade' ? light.map((x, i) => Math.round(x + (dark[i] - x) * progress)) : light;
    const lum = luminance(paper);
    const ink = contrast(lum, luminance(darkInk)) >= contrast(lum, luminance(lightInk)) ? darkInk : lightInk;
    body.style.setProperty('--paper', rgb(paper));
    body.style.setProperty('--ink', rgb(ink));
    body.style.setProperty('--subtle', rgb(ink));
    body.style.setProperty('--line', rgb(paper.map((x, i) => Math.round(x * .65 + ink[i] * .35))));
    body.style.setProperty('--focus', rgb(ink));
  }
  function schedule() {
    if (!pending) { pending = true; requestAnimationFrame(update); }
  }
  function refreshControl() {
    toggle.setAttribute('aria-pressed', String(enabled));
    toggle.textContent = enabled ? 'Effect on · turn off' : 'Effect off · turn on';
    schedule();
  }
  toggle.hidden = false;
  toggle.addEventListener('click', () => { enabled = !enabled; refreshControl(); });
  reduced.addEventListener('change', () => { enabled = !reduced.matches; refreshControl(); });
  addEventListener('scroll', schedule, { passive: true });
  addEventListener('resize', schedule);
  addEventListener('pageshow', schedule);
  // Markdown hydration, font loading and reflow can change the story's length.
  new ResizeObserver(schedule).observe(article);
  refreshControl();
  update();
})();
