#!/usr/bin/env python3
"""Regenerate published writing from Markdown: python3 tools/sync_poems.py [--check]."""
import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POEMS = ROOT / "poems"
ANIMATIONS = ["sequoia-upward-crawl-v1.html", "sequoia-upward-crawl-dusk.html",
              "sequoia-upward-crawl-bark.html", "sequoia-upward-crawl-signature.html"]
SOURCE = "/eng111_writing/poems/among-sequoia-sempervirens.md"

def parse(name):
    text = (POEMS / name).read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    text = re.sub(r"^present center aligned\s*\n+", "", text, flags=re.I)
    if name == "among-sequoia-sempervirens-inverted.md":
        footer = re.search(r'\n([^\n]+)\nby[ \t]+([^\n]+)$', text, flags=re.I)
        if footer:
            title, author = (part.strip() for part in footer.groups())
            body = re.sub(r'^# [^\n]+\n+', '', text[:footer.start()]).strip()
            text = '# ' + title + '\n\n' + body + '\n\n' + author + '\nby\n' + title
    heading = re.match(r"# ([^\n]+)\n+", text)
    if not heading:
        raise ValueError("Missing poem heading in " + name)
    title = heading.group(1)
    text = text[heading.end():]
    if name == "among-sequoia-sempervirens-inverted.md":
        footer = re.search(r'\n+([^\n]+)\nby[ \t]*\n([^\n]+)$', text.strip())
        if not footer:
            raise ValueError("Missing inverted poem footer in " + name)
        author, title = (part.strip() for part in footer.groups())
        body = text.strip()[:footer.start()]
        body = re.sub(r'^\*\*Reading instruction:\*\*[^\n]*\n*', '', body).strip()
        body = re.sub(r'^present center aligned[ \t]*\n*', '', body, flags=re.I).strip()
        stanzas = [(False, list(reversed([line.rstrip() for line in part.strip().split('\n')])))
                   for part in reversed(re.split(r'\n[ \t]*\n', body))]
        return title, author, stanzas
    byline = re.match(r"\*by ([^\n]+)\*\n+", text, flags=re.I)
    if not byline:
        raise ValueError("Missing byline in " + name)
    author = byline.group(1)
    text = text[byline.end():].strip()
    stanzas = []
    for part in re.split(r"\n[ \t]*\n", text):
        part = part.strip()
        italic = part.startswith("*") and part.endswith("*") and len(part) >= 2
        if italic:
            part = part[1:-1]
        lines = [line.rstrip(" \t") for line in part.split("\n")]
        if not all(lines):
            raise ValueError("Empty verse line in " + name)
        stanzas.append((italic, lines))
    return title, author, stanzas

def render(stanzas):
    blocks = []
    for italic, lines in stanzas:
        style = " stanza--italic" if italic else ""
        body = "\n".join('<span class="poem-line">' + html.escape(line, quote=False) +
                         "</span>" for line in lines)
        blocks.append('<p class="stanza' + style + '">\n' + body + "\n</p>")
    return "\n".join(blocks)

def replace_one(text, pattern, fn, label):
    result, count = re.subn(pattern, fn, text, flags=re.S)
    if count != 1:
        raise ValueError(label + ": expected one match, got " + str(count))
    return result

def sequoia_readings(current="standard"):
    base = "/eng111_writing/"
    items = [("standard", "poems/among-sequoia-sempervirens.html", "Read down"),
             ("inverted", "poems/among-sequoia-sempervirens-inverted.html", "Bidirectional"),
             ("interactive", "versions/sequoia-upward-crawl-bark.html", "Look up")]
    links = [('<span aria-current="page">' + label + '</span>') if key == current else
             ('<a href="' + base + path + '">' + label + '</a>') for key, path, label in items]
    return ('<nav class="reading-meta sequoia-readings" aria-label="Sequoia readings">' +
            '<span aria-hidden="true">·</span>'.join(links) + '</nav>')


def regenerate_page(path, names):
    source = path.read_text(encoding="utf-8")
    content = render(parse(names[0])[2])
    if names[0] == "among-sequoia-sempervirens.md":
        source = re.sub(r'<(?:div|nav) class="reading-meta[^"]*"[^>]*>.*?</(?:div|nav)>',
                        sequoia_readings(), source, count=1, flags=re.S)
    return replace_one(source, r'(<article class="verse[^"]*"[^>]*>).*?(</article>)',
                       lambda m: m[1] + "\n" + content + "\n" + m[2], str(path))


def regenerate_inverted_page():
    title, author, stanzas = parse("among-sequoia-sempervirens-inverted.md")
    visual = [(italic, list(reversed(lines))) for italic, lines in reversed(stanzas)]
    page = (POEMS / "among-sequoia-sempervirens.html").read_text(encoding="utf-8")
    page = page.replace('<title>', '<title>Inverted reading · ', 1)
    page = re.sub(r'<meta name="description"[^>]*>',
                  '<meta name="description" content="A static, bottom-to-top reading of Among Sequoia Sempervirens.">', page)
    page = re.sub(r'<div class="reading-hero">.*?</div></div>', '', page, flags=re.S)
    page = re.sub(r'<(?:div|nav) class="reading-meta[^"]*"[^>]*>.*?</(?:div|nav)>',
                  sequoia_readings("inverted"), page, count=1, flags=re.S)
    page = page.replace('data-poem-source="/eng111_writing/poems/among-sequoia-sempervirens.md"',
                        'data-poem-source="/eng111_writing/poems/among-sequoia-sempervirens-inverted.md" data-poem-order="inverted"')
    page = replace_one(page, r'(<article class="verse[^"]*"[^>]*>).*?(</article>)',
                       lambda m: m[1] + "\n" + render(visual) + "\n" + m[2], "inverted page")
    signature = ('<header class="inverted-signature"><h1 data-inverted-title>' + html.escape(title) +
                 '</h1><p>by <span data-inverted-author>' + html.escape(author) + '</span></p></header>')
    page = page.replace('</article></main>', '</article>' + signature + '</main>')
    page = page.replace('</head>', '<style>.inverted-signature{text-align:center;margin:24px auto 0;max-width:680px}'
                        '.inverted-signature p{font:20px/1.65 Georgia,serif;margin:6px 0 0}'
                        '.inverted-signature h1{font:400 clamp(22px,4vw,30px)/1.25 Georgia,serif;margin:0}</style></head>')
    return page.replace('assets/poem-live.js"', 'assets/poem-live.js?v=sequoia-static-2"')


def regenerate_animation(path):
    title, author, stanzas = parse("among-sequoia-sempervirens.md")
    lines = [line for _, group in stanzas for line in group]
    source = path.read_text(encoding="utf-8")
    array = ",\n    ".join(json.dumps(line, ensure_ascii=False) for line in lines)
    code = ("// POEM LINES START\n"
            "  const words = await window.PoemLive.lines('" + SOURCE + "', [\n"
            "    " + array + "\n  ]);\n  // POEM LINES END")
    source = replace_one(source, r"// POEM LINES START.*?// POEM LINES END",
                         lambda _: code, str(path))
    summary = html.escape(" / ".join(lines), quote=False)
    source = replace_one(source, r'(<p data-poem-summary>).*?(</p>)',
                         lambda m: m[1] + summary + m[2], str(path))
    source = replace_one(source, r'(<h1 class="title" id="title">).*?(</h1>)',
                         lambda m: m[1] + html.escape(title) + m[2], str(path))
    source = replace_one(source, r'(<div class="byline" id="byline">).*?(<br>by</div>)',
                         lambda m: m[1] + html.escape(author) + m[2], str(path))
    return source


def regenerate_story(path):
    source = path.with_suffix(".md").read_text(encoding="utf-8-sig").strip()
    heading = re.match(r"# ([^\n]+)\n+\*[Bb]y ([^\n]+)\*\n+", source)
    if not heading:
        raise ValueError("Missing story title or byline in " + str(path))
    title, author = map(html.escape, heading.groups())
    paragraphs = re.split(r"\n[ \t]*\n", source[heading.end():].strip())
    body = "\n".join("<p>" + html.escape(part, quote=False) + "</p>" for part in paragraphs)
    base = "/eng111_writing/"
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{title}, a short story by {author}."><title>{title} — {author}</title><script src="{base}assets/story-theme.js?v=2"></script><link rel="stylesheet" href="{base}assets/poems.css?v=marco-2"><link rel="stylesheet" href="{base}assets/reading-edition.css?v=20261024-5"></head>
<body class="theme-story edition"><header class="site-header"><a class="site-brand" href="{base}"><span class="site-brand__name">Michael Penta</span><span class="site-brand__sub">ENG 111 · Writing</span></a><nav class="site-nav" aria-label="Writing pages"><a href="{base}">Writing</a><a href="{base}poems/among-sequoia-sempervirens.html">Sequoia</a><a href="{base}poems/boston-proper.html">Boston</a><a href="{base}poems/olympic.html">Olympic</a><a href="{base}stories/{path.name}" aria-current="page">Marco Fragale</a></nav></header><hr class="site-divider">
<div class="reading-hero"><div class="reading-hero__inner"><h1>{title}</h1><p class="author">by {author}</p></div></div>
{story_experiments()}
<main class="reading-main"><div class="reading-meta"><a href="{base}">← All writing</a><label class="story-theme-control" hidden for="story-theme">Theme <select id="story-theme"><option value="molasses">Molasses flood</option><option value="lantern">Lantern light</option><option value="north-end">Old North End</option></select></label></div><article class="prose" aria-label="{title}" data-story-source="{base}stories/{path.stem}.md">
{body}
</article></main>
<footer class="site-footer"><p>© Michael Penta. All rights reserved.</p><p><a href="{base}">All writing</a> · <a href="https://github.com/pentaideas/eng111_writing">GitHub</a></p></footer><script src="{base}assets/poem-live.js"></script></body></html>
'''


    return page


def story_experiments(current="standard"):
    base = "/eng111_writing/"
    items = [("standard", "stories/the-unlikely-death-of-marco-fragale.html", "Standard"),
             ("lantern", "versions/marco-lantern-fades.html", "Lantern fades"),
             ("tide", "versions/marco-soft-tide.html", "Soft tide")]
    links = []
    for key, path, label in items:
        if key == current:
            links.append('<span aria-current="page">' + label + '</span>')
        else:
            links.append('<a href="' + base + path + '">' + label + '</a>')
    separator = '<span aria-hidden="true">·</span>'
    return ('<aside class="reading-versions" id="reading-versions">'
            '<nav aria-label="Marco reading versions">' + separator.join(links) + '</nav></aside>')


def regenerate_smooth_story(story, effect):
    page = regenerate_story(story)
    title = "Lantern fades" if effect == "lantern" else "Soft tide"
    page = page.replace('<title>', '<title>' + title + ' · ', 1)
    page = page.replace('<body class="theme-story edition">',
                        '<body class="theme-story edition marco-smooth" data-effect="' + effect + '">', 1)
    page = page.replace('<script src="/eng111_writing/assets/story-theme.js?v=2"></script>', '')
    page = page.replace('</head>', '<link rel="stylesheet" href="/eng111_writing/assets/marco-smooth.css?v=1">'
                        '<script defer src="/eng111_writing/assets/marco-smooth.js?v=1"></script></head>')
    page = re.sub(r'<label class="story-theme-control".*?</label>', '', page)
    page = page.replace(story_experiments(), story_experiments(effect))
    page = page.replace('</body>', '<div class="marco-scene" aria-hidden="true"><div class="marco-glow"></div>'
                        '<div class="marco-tide"></div></div>'
                        '<button class="marco-smooth-toggle" type="button" hidden aria-pressed="true">Effect on</button></body>')
    return page

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    targets = {
        POEMS / "among-sequoia-sempervirens-inverted.html": regenerate_inverted_page(),
        POEMS / "among-sequoia-sempervirens.html":
            regenerate_page(POEMS / "among-sequoia-sempervirens.html",
                            ["among-sequoia-sempervirens.md"]),
        POEMS / "boston-proper.html":
            regenerate_page(POEMS / "boston-proper.html", ["boston-proper.md"]),
        POEMS / "olympic.html":
            regenerate_page(POEMS / "olympic.html", ["olympic-v2.md"]),
        POEMS / "olympic-v1.html":
            regenerate_page(POEMS / "olympic-v1.html", ["olympic-v1.md"]),
    }
    for name in ANIMATIONS:
        path = ROOT / "versions" / name
        targets[path] = regenerate_animation(path)
    story = ROOT / "stories" / "the-unlikely-death-of-marco-fragale.html"
    targets[story] = regenerate_story(story)
    for effect, filename in [("lantern", "marco-lantern-fades.html"), ("tide", "marco-soft-tide.html")]:
        targets[ROOT / "versions" / filename] = regenerate_smooth_story(story, effect)
    different = []
    for path, result in targets.items():
        if not path.exists() or result != path.read_text(encoding="utf-8"):
            different.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(result, encoding="utf-8")
    if different:
        for name in different:
            print(("Out of sync: " if args.check else "Updated: ") + name)
    else:
        print("All published writing matches its source files.")
    return 1 if args.check and different else 0

if __name__ == "__main__":
    raise SystemExit(main())

