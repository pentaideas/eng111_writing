/* Browser-side poem sync; Markdown is always authoritative. */
(() => {
  'use strict';
  function parse(markdown, inverted = false) {
    let text = markdown.replace(/\r\n?/g, '\n').replace(/^\uFEFF/, '').trim();
    text = text.replace(/^present center aligned[ \t]*\n+/i, '');
    if (inverted) {
      const footer = text.match(/\n([^\n]+)\nby[ \t]+([^\n]+)$/i);
      if (footer) {
        const title = footer[1].trim(), author = footer[2].trim();
        const body = text.slice(0, footer.index).replace(/^# [^\n]+\n+/, '').trim();
        text = '# ' + title + '\n\n' + body + '\n\n' + author + '\nby\n' + title;
      }
    }
    const title = text.match(/^# ([^\n]+)\n+/);
    if (!title) throw new Error('Missing poem title');
    text = text.slice(title[0].length);
    if (inverted) {
      text = text.trim();
      const footer = text.match(/\n+([^\n]+)\nby[ \t]*\n([^\n]+)$/);
      if (!footer) throw new Error('Missing inverted poem footer');
      const body = text.slice(0, footer.index)
        .replace(/^\*\*Reading instruction:\*\*[^\n]*\n*/, '').trim()
        .replace(/^present center aligned[ \t]*\n*/i, '').trim();
      if (!body) throw new Error('Empty inverted poem');
      const stanzas = body.split(/\n[ \t]*\n/).reverse().map(part => ({
        italic: false,
        lines: part.trim().split('\n').map(line => line.replace(/[ \t]+$/g, '')).reverse()
      }));
      return { title: footer[2].trim(), author: footer[1].trim(), stanzas,
        lines: stanzas.flatMap(stanza => stanza.lines) };
    }
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
    return parse(await response.text(), path.endsWith('-inverted.md'));
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
      const inverted = element.dataset.poemOrder === 'inverted';
      const stanzas = inverted ? [...poem.stanzas].reverse() : poem.stanzas;
      const nodes = stanzas.map(stanza => {
        const block = document.createElement('p');
        block.className = 'stanza' + (stanza.italic ? ' stanza--italic' : '');
        const lines = inverted ? [...stanza.lines].reverse() : stanza.lines;
        lines.forEach(line => {
          const span = document.createElement('span');
          span.className = 'poem-line';
          span.textContent = line;
          block.appendChild(span);
        });
        return block;
      });
      if (nodes.length) element.replaceChildren(...nodes);
      if (inverted) {
        document.querySelector('[data-inverted-author]').textContent = poem.author;
        document.querySelector('[data-inverted-title]').textContent = poem.title;
      }
    } catch (error) {
      console.warn('Using published poem fallback:', error);
    }
  }
  function hydrate() {
    document.querySelectorAll('[data-poem-source]').forEach(updateReading);
    document.querySelectorAll('[data-story-source]').forEach(async element => {
      try {
        const path = element.dataset.storySource;
        if (!/^\/eng111_writing\/stories\/[\w-]+\.md$/.test(path))
          throw new Error('Unexpected story source path');
        const response = await fetch(path, { cache: 'no-store' });
        if (!response.ok) throw new Error('Story unavailable: ' + response.status);
        const text = (await response.text()).replace(/\r\n?/g, '\n').replace(/^\uFEFF/, '').trim();
        const heading = text.match(/^# ([^\n]+)\n+\*[Bb]y ([^\n]+)\*\n+/);
        if (!heading) throw new Error('Missing story title or byline');
        const body = text.slice(heading[0].length).trim();
        if (!body) throw new Error('Empty story');
        const paragraphs = body.split(/\n[ \t]*\n/).map(part => {
          const paragraph = document.createElement('p');
          paragraph.textContent = part;
          return paragraph;
        });
        element.replaceChildren(...paragraphs);
      } catch (error) {
        console.warn('Using published story fallback:', error);
      }
    });
  }
  window.PoemLive = { parse, load, lines, hydrate };
  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', hydrate, { once: true });
  else hydrate();
})();
