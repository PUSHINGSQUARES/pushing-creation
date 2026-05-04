---
description: Scaffold a new cinematic project with starter style and storyboard templates
argument-hint: "<project-slug> (e.g. 'bmw-track-day', 'editorial-portrait', 'product-launch')"
---

Parse `$ARGUMENTS` as the project slug. If empty, ask the user for a project name (lowercase, hyphens, no spaces).

## Steps

1. **Create the project folder** at `projects/<slug>/` relative to the repo root.

2. **Copy templates:**
   - `templates/style.md` to `projects/<slug>/style.md`
   - `templates/storyboard.md` to `projects/<slug>/storyboard.md`

3. **Create the refs folder** at `projects/<slug>/refs/` with a `.gitkeep` inside it.

4. **Report what was created:**

```
Created projects/<slug>/
  style.md        starter STYLE_/NEG_ block library
  storyboard.md   BMW worked example (replace with your shots)
  refs/            drop reference images here
```

5. **Tell the user what to do next:**
   - Drop reference stills, plates, and mood frames into `refs/`.
   - Open `style.md` and customize the STYLE_/NEG_ blocks to match their visual voice. The starter library covers common AI failure modes. Override block bodies with their own language.
   - Replace the BMW example shots in `storyboard.md` with their own shot list. Follow the same format: camera, lens, action, style refs, neg refs.
   - When `/frames-brainstorm` ships (v0.2), it will interview them with their reference images to write `style.md` live. Until then, hand-edit using the guidance in the skill.

Do NOT create any files outside `projects/<slug>/`. Do NOT modify templates.
