---
name: pushing-creation
description: Cinematic prompt methodology for AI image and video generation. Activates when the user mentions cinematic projects, shot lists, shoot briefs, storyboards, style packs, or visual generation workflows.
---

# PUSHING CREATION_

Cinematic prompt methodology workspace. You're helping a user author **style packs** and **storyboards** that produce professional-grade AI-generated images and video.

## The thesis

> Stop prompting. Start defining outcomes.

Treat the AI like a **director of photography** you've hired. You don't tell a DP "make it cinematic." You tell them ARRI Alexa 35, 50mm prime at T1.5, golden-hour rim from frame right, anamorphic squeeze, 24fps at 1/48 shutter, and you hand them three reference images.

**Specificity transfers craft.** Years of being on set compressed into a sentence the model can act on. Vague prompts produce average results because models default to the average of their training data.

## Three principles

- **Brief the DP.** Camera, rig, lens, T-stop, shutter, fps, lighting state and direction, focal subject, time of day. Every field a real DP would need on the day.
- **References do the heavy lifting.** Words narrow. Images aim. Drop reference stills for skin tone, fabric, livery, location mood.
- **Negative blocks fight defaults.** The plastic-skin centred-front-lit hero is the AI's default because it's the average of training data. Pull against that average loudly and consistently.

## Project format

Every project is a folder with three things:

```
projects/<slug>/
  style.md        # STYLE_ and NEG_ blocks (the visual voice)
  storyboard.md   # shot table (camera, lens, action, style refs)
  refs/            # reference images
```

### `style.md`

Named blocks prefixed `STYLE_` (positive) or `NEG_` (negative). Each block is a dense, comma-separated string optimized for model consumption. The block name describes intent; the body is the prompt fragment.

**STYLE_ blocks** define the visual voice: film stock, lighting state, lens character, grain, composition rules. **NEG_ blocks** fight specific AI failure modes: plastic skin, centred composition, flat lighting, anatomy glitches.

Mix blocks per shot. A macro close-up needs `STYLE_MACRO_TACTILE` + `STYLE_GRAIN_HALATION` but not `STYLE_ANAMORPHIC`. Fewer, targeted blocks beat stacking everything.

### `storyboard.md`

A markdown table with columns: `Shot | Provider | Model | Camera | Lens | Aspect | Action | Refs | Style | Neg | Mode | Duration`

The **Action** column is the prompt. Lead with `Shot on [camera] mounted on [rig]`. State T-stop, shutter speed, ISO, fps. Then describe the scene with the precision a DP brief demands.

The **Style** and **Neg** columns reference block names from `style.md`. The generation tool (or the user) expands these into the full prompt at render time.

### `refs/`

Reference stills, plates, mood frames. Drop images here. `/frames-brainstorm` reads them via vision to ground style interviews in real visual material.

## Authoring guidance (hand-editing)

When helping a user author `style.md` by hand:

1. **Start from the starter template** (`templates/style.md`). It ships a curated STYLE_/NEG_ library covering the most common AI failure modes.
2. **Interview for their voice.** Ask about: visual references (films, photographers), colour palette (warm/cool, film stock), grain and texture, camera and lens preferences, subject-specific negatives, prompting tricks they've found reliable.
3. **Be specific, not decorative.** "ARRI Alexa 35, 50mm at T1.5, golden-hour rim from frame right" beats "cinematic golden hour lighting." Every word should change what the model renders.
4. **Test negative blocks.** Generate without negs, then with. The difference should be visible and consistent.

### Using `/frames-brainstorm`

The interactive alternative to hand-editing. The user drops reference images into `projects/<slug>/refs/`, runs `/frames-brainstorm`, and Claude conducts a DP-voiced interview grounded in vision analysis of those refs. Each answer gets compressed into a STYLE_ or NEG_ block and written to `style.md` in real time. The user talks naturally about their visual taste; Claude listens, compresses, writes. Aim for 6-10 blocks per session.

### Using `/frames-shotlist`

The storyboard generator. Reads `style.md` block names, analyses reference images via vision, gathers the project concept (from `CONCEPT.md` or by asking), and drafts a full shot table. Each row is a self-contained brief with camera, lens, T-stop, action description, and style/neg references. Default target is 6-10 shots. Run after `/frames-brainstorm` to go from visual voice to shot-by-shot execution plan.

### Using `/frames-shot`

The single-shot editor. Pass a shot number to refine an existing row, or `new` to append. DP-voiced conversation that pushes back on vague input and compresses feedback into the storyboard table. Uses Edit tool to modify only the target row, preserving table integrity.

When helping author `storyboard.md`:

1. **One row per shot.** Each shot is a self-contained brief.
2. **Camera and lens first.** These set the spatial and depth-of-field baseline before the scene description.
3. **Aspect ratio matters.** 21:9 for cinematic wides, 16:9 for action, 4:5 or 9:16 for social.
4. **Reference images per shot.** If a shot depends on a specific visual anchor (a hand pose, a car livery, a location), name the ref file in the Refs column.

## Templates and examples

- `templates/style.md` is the **starter STYLE_/NEG_ library**. Curated blocks fighting the most common AI defaults.
- `templates/storyboard.md` is a **worked BMW M-Series Track Day example**. Six shots showing the format end-to-end.
- `templates/example-project/` is the **full BMW pack** with style, storyboard, and refs folder.

## Available commands

- `/frames-new <slug>` scaffolds a new project folder with starter templates.
- `/frames-brainstorm` runs a vision-grounded DP interview that writes `style.md` live from your reference images.
- `/frames-shotlist` generates a full storyboard from style + refs + concept.
- `/frames-shot <N>` authors or refines a single shot in the storyboard.

## Relationship to PUSHING FRAMES

This workspace is the methodology. [PUSHING FRAMES](https://github.com/PUSHINGSQUARES/pushing-frames) is the generation tool. They're siblings, not dependencies. Projects authored here open cleanly in PUSHING FRAMES. You don't need PUSHING FRAMES to use this workspace, and you don't need this workspace to use PUSHING FRAMES.
