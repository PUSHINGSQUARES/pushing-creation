# Keychain Setup

pushing-creation reads API keys from macOS Keychain at call time. Claude never sees the key value. The secret is read into a Python variable inside the CLI process and passed straight to the provider's HTTP client. Nothing key-shaped lands in Claude's transcript, your shell history, or any log.

## Why Keychain

- **Zero-trust for Claude.** The model receives only the generation output, not the key.
- **OS-level encryption.** Keys are stored encrypted at rest and access-controlled per application.
- **No env-var leak risk.** No `.env` file to accidentally commit or expose in a subprocess dump.
- **macOS-native.** No password manager, no extra tooling. One command per provider.

## Adding a key

The recommended way is through the CLI, which handles the correct storage format:

```sh
bin/frames-keys add <provider>
```

You'll be prompted for your key with hidden input. The key is stored under `com.shadow.control / apiKey_<provider>` in your login Keychain.

Supported providers: `gemini`, `openai`, `openrouter`, `kling`, `seedream`, `seedance`, `imagen`

---

If you prefer to add keys manually, use this format:

```sh
security add-generic-password -U \
  -s "com.shadow.control" \
  -a "apiKey_<provider>" \
  -w "[YOUR_KEY]"
```

For example, for Gemini:

```sh
security add-generic-password -U \
  -s "com.shadow.control" \
  -a "apiKey_gemini" \
  -w "AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

Get your Gemini key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

### Key formats by provider

| Provider | Key format | Where to get it |
|----------|-----------|-----------------|
| gemini | `AIza...` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| openai | `sk-...` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| openrouter | `sk-or-v1-...` | [openrouter.ai/keys](https://openrouter.ai/keys) |
| kling | `AKXXXXXXXX:secretXXXXXX` | [klingai.com](https://klingai.com) under API settings |
| seedream | `access_key:secret_key` | [console.volcengine.com](https://console.volcengine.com) under Access Control |
| seedance | Same Volcano Engine credentials as seedream | Same as above |
| imagen | `project-id:ya29.XXXXXXXX` | [cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai) (access token expires after 1h) |

## Verifying a key

Test that the key works with a live API ping:

```sh
bin/frames-keys test gemini
```

List stored provider keys without revealing values:

```sh
bin/frames-keys list
```

## Updating a key

Re-run `frames-keys add <provider>` with your new key. It updates the existing entry.

## Removing a key

```sh
bin/frames-keys remove gemini
```

This removes the key from both the primary (`com.shadow.control`) and legacy (`pushing-creation:*`) schemes if present.

## Legacy entries

If you added keys before v0.3.0 using raw `security add-generic-password -s "pushing-creation:<provider>"` commands, they still work. The CLI checks both schemes and uses whichever is found. New keys added via `frames-keys add` go into the primary scheme.

## macOS-only note

The `security` CLI is macOS-specific. Linux and Windows secret backends (libsecret, Windows Credential Manager) are planned for a future release. Until then, the CLI will print a clear error if `security` is not available.
