#!/usr/bin/env python3
"""Regenerate published poems from poems/*.md: python3 tools/sync_poems.py [--check]."""
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
    heading = re.match(r"# ([^\n]+)\n+", text)
    if not heading:
        raise ValueError("Missing poem heading in " + name)
    title = heading.group(1)
    text = text[heading.end():]
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

def regenerate_page(path, names):
    source = path.read_text(encoding="utf-8")
    if path.name != "olympic.html":
        content = render(parse(names[0])[2])
        return replace_one(source, r'(<article class="verse[^"]*"[^>]*>).*?(</article>)',
                           lambda m: m[1] + "\n" + content + "\n" + m[2], str(path))
    for number, name in enumerate(names, 1):
        content = render(parse(name)[2])
        pattern = (r'(<section class="draft-section" id="version-' + str(number) +
                   r'"[\s\S]*?<div class="verse"[^>]*>).*?(</div>)')
        source = replace_one(source, pattern,
                             lambda m: m[1] + "\n" + content + "\n" + m[2], str(path))
    return source

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    targets = {
        POEMS / "among-sequoia-sempervirens.html":
            regenerate_page(POEMS / "among-sequoia-sempervirens.html",
                            ["among-sequoia-sempervirens.md"]),
        POEMS / "boston-proper.html":
            regenerate_page(POEMS / "boston-proper.html", ["boston-proper.md"]),
        POEMS / "olympic.html":
            regenerate_page(POEMS / "olympic.html", ["olympic-v1.md", "olympic-v2.md"]),
    }
    for name in ANIMATIONS:
        path = ROOT / "versions" / name
        targets[path] = regenerate_animation(path)
    different = []
    for path, result in targets.items():
        if result != path.read_text(encoding="utf-8"):
            different.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(result, encoding="utf-8")
    if different:
        for name in different:
            print(("Out of sync: " if args.check else "Updated: ") + name)
    else:
        print("All published poem copies match their source files.")
    return 1 if args.check and different else 0

if __name__ == "__main__":
    raise SystemExit(main())
