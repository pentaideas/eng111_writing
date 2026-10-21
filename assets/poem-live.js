/* Browser-side poem sync; Markdown is always authoritative. */
(() => {
  'use strict';
  function parse(markdown) {
    let text = markdown.replace(/\r\n?/g, '\n').replace(/^\uFEFF/, '').trim();
    text = text.replace(/^present center aligned[ \t]*\n+/i, '');
    const title = text.match(/^# ([^\n]+)\n+/);
    if (!title) throw new Error('Missing poem title');
    text = text.slice(title[0].length);
    const author = text.match(/^\*by ([^\n]+)\*\n+/i);
    if (!author) throw new Error('Missing poet byline');
    text = text.slice(author[0].length).trim();
    const stanzas = text.split(/\n[ \t]*\n/).map(part => {
      part = part.trim();
      const italic = part.startsWith('*') && part.endsWith('*') && part.length >= 2;
      if (italic) part = part.slice(1, -1);
      return { italic, lines: part.split('\n').map(line => line.replace(/[ \t]+$/g, '')) };
    });
    return { title: title[1], author: author[1], stanzas,
      lines: stanzas.flatMap(stanza => stanza.lines) };
  }
  async function load(path) {
    if (!/^\/eng111_writing\/poems\/[\w-]+\.md$/.test(path))
      throw new Error('Unexpected poem source path');
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) throw new Error('Poem unavailable: ' + response.status);
    return parse(await response.text());
  }
  async function lines(path, fallback) {
    try {
      const poem = await load(path);
      if (!poem.lines.length) throw new Error('Empty poem');
      const summary = document.querySelector('[data-poem-summary]');
      if (summary) summary.textContent = poem.lines.join(' / ');
      return poem.lines;
    } catch (error) {
      console.warn('Using published poem fallback:', error);
      return fallback;
    }
  }
  async function updateReading(element) {
    try {
      const poem = await load(element.dataset.poemSource);
      const nodes = poem.stanzas.map(stanza => {
        const block = document.createElement('p');
        block.className = 'stanza' + (stanza.italic ? ' stanza--italic' : '');
        stanza.lines.forEach(line => {
          const span = document.createElement('span');
          span.className = 'poem-line';
          span.textContent = line;
          block.appendChild(span);
        });
        return block;
      });
      if (nodes.length) element.replaceChildren(...nodes);
    } catch (error) {
      console.warn('Using published poem fallback:', error);
    }
  }
  function hydrate() {
    document.querySelectorAll('[data-poem-source]').forEach(updateReading);
  }
  window.PoemLive = { parse, load, lines, hydrate };
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', hydrate, { once: true });
  else hydrate();
})();
