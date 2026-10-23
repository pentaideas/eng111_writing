/* New variations have their own renderer so the original experiments stay intact. */
(() => {
  'use strict';
  const article = document.querySelector('[data-story-source]');
  const control = document.querySelector('.marco-smooth-toggle');
  const glow = document.querySelector('.marco-glow');
  const tide = document.querySelector('.marco-tide');
  if (!article || !control || !glow || !tide) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let enabled = !reduced.matches;
  let start = 0, end = 1, target = 0, current = 0;
  let frame = 0, previous = 0;
  const clamp = value => Math.max(0, Math.min(1, value));
  function paint() {
    // Ease the atmosphere, never the document or the reader's scrolling.
    const eased = current * current * (3 - 2 * current);
    glow.style.opacity = String(1 - eased);
    glow.style.transform = `scale(${1 - eased * .18})`;
    tide.style.transform = `translate3d(0,${100 * (1 - eased)}%,0)`;
  }
  function animate(time) {
    const elapsed = previous ? Math.min(64, time - previous) : 16;
    previous = time;
    current += (target - current) * (1 - Math.exp(-elapsed / 110));
    if (Math.abs(target - current) < .0001) {
      current = target; frame = 0; previous = 0; paint(); return;
    }
    paint();
    frame = requestAnimationFrame(animate);
  }
  function followScroll(immediate = false) {
    target = enabled ? clamp((scrollY - start) / Math.max(1, end - start)) : 0;
    if (immediate) {
      if (frame) cancelAnimationFrame(frame);
      frame = 0; previous = 0; current = target; paint();
    } else if (!frame && Math.abs(target - current) >= .0001) {
      frame = requestAnimationFrame(animate);
    }
  }
  function measure() {
    const rect = article.getBoundingClientRect();
    start = rect.top + scrollY - innerHeight * .3;
    end = rect.bottom + scrollY - innerHeight * .8;
    followScroll(true);
  }
  function refresh() {
    control.setAttribute('aria-pressed', String(enabled));
    control.textContent = enabled ? 'Effect on · turn off' : 'Effect off · turn on';
    followScroll(true);
  }
  control.hidden = false;
  control.addEventListener('click', () => { enabled = !enabled; refresh(); });
  reduced.addEventListener('change', () => { enabled = !reduced.matches; refresh(); });
  addEventListener('scroll', () => followScroll(), { passive: true });
  addEventListener('resize', measure);
  addEventListener('pageshow', measure);
  new ResizeObserver(measure).observe(article);
  if (document.fonts) document.fonts.ready.then(measure);
  measure();
  refresh();
})();
