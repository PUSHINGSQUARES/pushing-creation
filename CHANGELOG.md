# Changelog

## v0.3.0 -- 2026-05-08

### Added
- bin/frames-gen CLI for direct provider generation from Claude Code, reading API keys from macOS Keychain.
- bin/frames-keys helper for adding/listing/testing/removing provider keys.
- /frames-gen and /frames-keys Claude Code commands.
- Provider implementations: Gemini (Flash image + Veo 2 video), OpenAI (GPT-image-1), OpenRouter, Kling, Seedream, Seedance, Imagen (Vertex AI).
- lib/keychain.py -- macOS Keychain wrapper (security CLI).
- lib/scrub.py -- response and error sanitiser that redacts key-shaped strings.
- lib/storyboard.py -- storyboard.md shot table parser.
- lib/style.py -- style.md STYLE_/NEG_ block parser.
- docs/KEYCHAIN_SETUP.md -- per-provider setup guide with placeholder examples.
- docs/PROVIDERS.md -- supported providers, status, Keychain service names, cost notes.

### Notes
- macOS only. Linux/Windows secret backends planned.
- Stdlib-only Python 3.9+. No pip install required for end users.
- Tests require pytest (development dep, not user-facing).
- `imagen` provider scaffolded but not yet wired to a live key. Set up with `bin/frames-keys add imagen` once a Google Imagen key is available.
- `seedream` and `seedance` providers scaffolded. Keys stored in Keychain are UUID-format; correct API endpoint unconfirmed. Deferred to v0.3.x once endpoint is resolved.
