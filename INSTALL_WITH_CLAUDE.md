# Instructions for Claude

You're operating with **pushing-creation** loaded, a cinematic prompt methodology for AI image and video generation.

## What's available

- **`.claude/skills/pushing-creation/SKILL.md`** contains the full methodology: the DP-as-director thesis, project format, authoring guidance, and block conventions. Read it when helping with any cinematic authoring task.
- **`.claude/commands/frames-new.md`** is the `/frames-new <slug>` command that scaffolds new projects.
- **`.claude/commands/frames-brainstorm.md`** is the `/frames-brainstorm` command that runs a vision-grounded DP interview.
- **`.claude/agents/dp-interlocutor.md`** is the autonomous subagent for delegated style pack authoring.
- **`templates/style.md`** is the starter STYLE_/NEG_ block library.
- **`templates/storyboard.md`** is a worked BMW example showing the shot table format.
- **`templates/example-project/`** is the full BMW pack (style + storyboard + refs folder).

## What to do when the user arrives

1. Confirm they have pushing-creation loaded and explain what's available: a methodology for authoring cinematic style packs and storyboards, with starter templates and a worked example.
2. Offer to scaffold their first project with `/frames-new <project-slug>`.
3. Once they have a project with reference images in `refs/`, offer `/frames-brainstorm` to interview them and write `style.md` live.
4. If they want to explore the methodology first, point them to the example project in `templates/example-project/` and the skill for authoring guidance.

## Current version (v0.2)

Available commands:

- `/frames-new <slug>` scaffolds a new project.
- `/frames-brainstorm` runs a vision-grounded DP interview that writes `style.md` live from reference images.

Coming soon:

- `/frames-shotlist` (v0.3) will generate a full storyboard from concept + style.
- `/frames-shot` (v0.3) will author or edit individual shots.

## Key principle

> Stop prompting. Start defining outcomes.

Every style block and shot description should read like a brief you'd hand to a director of photography on set. Camera, lens, T-stop, shutter, lighting state, direction. Specificity transfers craft. Vague transfers nothing.
