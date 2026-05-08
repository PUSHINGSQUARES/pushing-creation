---
description: Generate an image or video for a storyboard shot using a provider via macOS Keychain
argument-hint: "<shot-N> (e.g. '1', '3') or a shot ID from storyboard.md"
---

Generate a storyboard shot by running bin/frames-gen with API keys read from Keychain.

## Steps

1. Confirm project files exist. Check that style.md and storyboard.md are present in the current working directory. If not, tell the user to run /frames-new first or navigate to their project folder.

2. Parse the shot. Read the relevant row from storyboard.md to determine whether it is an image or video shot (check the Mode column; if blank, check Duration -- a non-empty duration means video) and the shot's aspect ratio from the Aspect column.

3. Determine the provider. In order: use the Provider column value if non-empty, check _config/default-provider in the project folder if it exists, or ask the user. Available providers: gemini, openai, openrouter, kling, seedream, seedance, imagen.

4. Confirm kind matches provider. If the shot is video and the chosen provider doesn't support video (openai, openrouter, seedream, imagen), ask the user to pick a video-capable provider (gemini, kling, seedance).

5. Determine output path. Use renders/shot-N.ext where ext is png for images, mp4 for videos.

6. Run the CLI:

```
bin/frames-gen --provider <provider> --kind <image|video> --shot-n <N> --out renders/shot-N.ext
```

7. Surface the result. Print only the output path from stdout. Do NOT echo any provider response body.

8. If it fails: exit code 2 means missing Keychain entry -- tell the user to run bin/frames-keys add <provider>. Exit code 3 is a provider HTTP error. Exit code 4 is invalid args.
