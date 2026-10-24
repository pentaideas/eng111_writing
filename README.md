# ENG 111 Writing — Michael Penta

An archive of drafts of original poems and short fiction for ENG 111.

**[Read the writing on the website](https://pentaideas.github.io/eng111_writing/)**

## Poems

- [Among Sequoia Sempervirens](https://pentaideas.github.io/eng111_writing/poems/among-sequoia-sempervirens.html)
- [Boston Proper](https://pentaideas.github.io/eng111_writing/poems/boston-proper.html)
- [Olympic](https://pentaideas.github.io/eng111_writing/poems/olympic.html) — [alternate draft](https://pentaideas.github.io/eng111_writing/poems/olympic-v1.html)

## Stories

- [The Unlikely Death of Marco Fragale](https://pentaideas.github.io/eng111_writing/stories/the-unlikely-death-of-marco-fragale.html) 

## Experiments in Presentation 
### Reading Direction and Looking Up

I wanted *Among Sequoia Sempervirens* to be read from the bottom up, reflecting the action of looking up a tree. I’ve kept four versions as I work toward that experience, each with a choice of three color schemes.

**[Read upward](https://pentaideas.github.io/eng111_writing/versions/sequoia-upward-crawl-bark.html)**

[Try all four upward-reading experiments](https://pentaideas.github.io/eng111_writing/versions/random.html)

### Darkness Consumes

Two ways to experience the story’s growing darkness:

- [Lantern fades](https://pentaideas.github.io/eng111_writing/versions/marco-lantern-fades.html) — a warm glow slowly goes out.
- [Soft tide](https://pentaideas.github.io/eng111_writing/versions/marco-soft-tide.html) — darkness rises with a softer edge.

Scroll back up to reverse the effect, or use the on/off button.

## Reading pages

The main pages use a compact reading layout with flat color fields. Boston retains its intentional Red Sox navy and red on its reading page; its homepage cover uses a pale ground and the same plain reading link as the other poems. Marco has a single navigation line for Standard, Lantern fades, and Soft tide, with the current reading marked. Olympic opens Version 2, with Version 1 available as an alternate draft.

These pages and the homepage load `assets/reading-edition.css`. Sequoia uses the existing Redwood Bark upward-reading experiment; all four original experiments remain available unchanged.

Markdown remains the source for published writing. The standard Sequoia page and all four interactive upward readings use `poems/among-sequoia-sempervirens.md`. The separate [static inverted reading](https://pentaideas.github.io/eng111_writing/poems/among-sequoia-sempervirens-inverted.html) uses `poems/among-sequoia-sempervirens-inverted.md`, preserving its visual line order and author / by / title footer. The two drafts can differ. Standard and static inverted pages share a compact reading switcher; the homepage and interactive menus link directly to the static inverted reading. Run `python3 tools/sync_poems.py` after text changes, then `python3 tools/sync_poems.py --check` to verify the generated pages. Marco’s layout and version menu are maintained in that script.

## Rights

All works © Michael Penta. All rights reserved.

