# Keychain Setup

pushing-creation reads API keys from macOS Keychain at call time. Claude never sees the key value. The secret is read into a Python variable inside the CLI process and passed straight to the provider's HTTP client. Nothing key-shaped lands in Claude's transcript, your shell history, or any log.

## Why Keychain

- **Zero-trust for Claude.** The model receives only the generation output, not the key.
- **OS-level encryption.** Keys are stored encrypted at rest and access-controlled per application.
- **No env-var leak risk.** No `.env` file to accidentally commit or expose in a subprocess dump.
- **macOS-native.** No password manager, no extra tooling. One `security` command per provider.

## Adding a key

Use `security add-generic-password` with the `-U` flag (update if exists). Replace the placeholder with your real key.

### Gemini (Google AI Studio)

```sh
security add-generic-password -U \
  -s "pushing-creation:gemini" \
  -a "$USER" \
  -w "[YOUR_GOOGLE_AI_STUDIO_KEY]"
```

Get your key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

### OpenAI

```sh
security add-generic-password -U \
  -s "pushing-creation:openai" \
  -a "$USER" \
  -w "[YOUR_OPENAI_API_KEY]"
```

Get your key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### OpenRouter

```sh
security add-generic-password -U \
  -s "pushing-creation:openrouter" \
  -a "$USER" \
  -w "[YOUR_OPENROUTER_KEY]"
```

Get your key at [openrouter.ai/keys](https://openrouter.ai/keys).

### Kling

```sh
security add-generic-password -U \
  -s "pushing-creation:kling" \
  -a "$USER" \
  -w "[YOUR_KLING_API_KEY]"
```

Get your key at [klingai.com](https://klingai.com) under API settings.

### Seedream (Bytedance)

Seedream uses Volcano Engine HMAC signing. The key format is `access_key:secret_key`.

```sh
security add-generic-password -U \
  -s "pushing-creation:seedream" \
  -a "$USER" \
  -w "[VOLCANO_ACCESS_KEY]:[VOLCANO_SECRET_KEY]"
```

Get credentials at [console.volcengine.com](https://console.volcengine.com) under Access Control.

### Seedance (Bytedance)

Same Volcano Engine credentials as Seedream. You can use the same access/secret key pair if your account has both services enabled.

```sh
security add-generic-password -U \
  -s "pushing-creation:seedance" \
  -a "$USER" \
  -w "[VOLCANO_ACCESS_KEY]:[VOLCANO_SECRET_KEY]"
```

### Imagen (Google Vertex AI)

Imagen uses Vertex AI. The key format is `project_id:access_token`. Access tokens expire after 1 hour; obtain a fresh one with `gcloud auth print-access-token`.

```sh
security add-generic-password -U \
  -s "pushing-creation:imagen" \
  -a "$USER" \
  -w "my-gcp-project-id:ya29.[YOUR_GCLOUD_ACCESS_TOKEN]"
```

Your GCP project must have the Vertex AI API enabled and the `imagegeneration@006` model available. See [cloud.google.com/vertex-ai/generative-ai/docs/image/overview](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview).

## Verifying a key

Check the entry exists without revealing its value:

```sh
security find-generic-password -s "pushing-creation:gemini"
```

macOS will prompt for Keychain access the first time. Subsequent access by the same binary is allowed without prompting.

Test that the key works with a live API ping:

```sh
bin/frames-keys test gemini
```

## Listing stored keys

```sh
bin/frames-keys list
```

This prints service names only. No values are shown.

## Updating a key

Re-run the `security add-generic-password -U` command with the new value. The `-U` flag updates an existing entry rather than creating a duplicate.

## Removing a key

```sh
bin/frames-keys remove gemini
```

## macOS-only note

The `security` CLI is macOS-specific. Linux and Windows secret backends (libsecret, Windows Credential Manager) are planned for a future release. Until then, the CLI will print a clear error if `security` is not available.
