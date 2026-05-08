# Providers

pushing-creation supports direct generation through these providers.

## Verification matrix

| Provider | Image | Video | Verified | Notes |
|----------|-------|-------|----------|-------|
| gemini | yes | yes | ✓ verified 2026-05-08 (image) | Gemini 2.5 Flash image via Google AI Studio |
| openai | yes | no | ✓ verified 2026-05-08 | GPT-image-1; no video support |
| openrouter | yes | no | scaffolded, unverified — model availability varies by plan | Pass-through; default model requires account with image tier |
| kling | no | yes | ✓ verified 2026-05-08 | Kling v2 Master video; JWT signed with HMAC-SHA256 |
| seedream | yes | no | scaffolded, unverified — ARK API key format mismatch | Stored key is ARK UUID; provider expects Volcengine HMAC. Deferred to v0.3.x. |
| seedance | no | yes | scaffolded, unverified — ARK API key format mismatch | Same as seedream; deferred to v0.3.x. |
| imagen | yes | no | scaffolded, unverified — requires Vertex AI auth, deferred to v0.3.x | Google Imagen 006 via Vertex AI |

## Provider details

### Gemini

- **Keychain service:** `pushing-creation:gemini`
- **Image model:** `gemini-2.5-flash-image`
- **Video model:** `veo-2.0-generate-001`
- **Cost:** Image approximately $0.002 per image; Veo video approximately $0.05-0.30 per second
- **Auth:** Google AI Studio API key (`AIza...`)
- **Where to get:** [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### OpenAI

- **Keychain service:** `pushing-creation:openai`
- **Image model:** `gpt-image-1`
- **Video:** Not supported
- **Cost:** Approximately $0.02-0.04 per image depending on size
- **Auth:** OpenAI API key (`sk-...`)
- **Where to get:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### OpenRouter

- **Keychain service:** `pushing-creation:openrouter`
- **Default image model:** `black-forest-labs/flux-1.1-pro`
- **Video:** Not supported
- **Cost:** Varies by underlying model; check [openrouter.ai/models](https://openrouter.ai/models)
- **Auth:** OpenRouter API key (`sk-or-v1-...`)
- **Where to get:** [openrouter.ai/keys](https://openrouter.ai/keys)
- **Quirk:** Override model via `--extras model=<model-id>` in the CLI

### Kling

- **Keychain service:** `pushing-creation:kling`
- **Video model:** `kling-v2-master`
- **Image:** Not supported
- **Cost:** Approximately $0.14 per 5-second clip (varies by tier)
- **Auth:** Kling AccessKey + SecretKey; signed as HMAC-SHA256 JWT per call
- **Key format:** `AKXXXXXXXX:secretXXXXXX` (colon-separated access_key:secret_key)
- **Where to get:** [klingai.com](https://klingai.com) under API settings
- **Quirk:** Generation is async; CLI polls until complete (up to 10 minutes). JWT is generated fresh each request using stdlib `hmac`/`hashlib` — no third-party dependency.

### Seedream

- **Keychain service:** `pushing-creation:seedream`
- **Image model:** `seedream-v3`
- **Video:** Not supported. Use seedance for video.
- **Auth:** Volcano Engine `access_key:secret_key` (HMAC-SHA256 signed)
- **Key format:** Store as `AKXXXXXXXX:secretXXXXXX` (colon-separated)
- **Where to get:** (https://www.byteplus.com/en) under Access Control
- **Quirk:** Bytedance request signing requires timestamp-based HMAC. Key is two parts separated by colon.

### Seedance

- **Keychain service:** `pushing-creation:seedance`
- **Video model:** `seedance-v1-lite`
- **Image:** Not supported. Use seedream for images.
- **Auth:** Same Volcano Engine `access_key:secret_key` as Seedream
- **Key format:** `AKXXXXXXXX:secretXXXXXX`
- **Where to get:** (https://www.byteplus.com/en)
- **Quirk:** Seedance falls back to the Seedream Keychain entry when no separate seedance entry is set, since both run on Volcengine ARK with shared credentials. If you only have one Volcengine key, storing it under `pushing-creation:seedream` covers both providers.

### Imagen

> **Status: scaffolded, unverified — requires Vertex AI auth, deferred to v0.3.x**
>
> The provider code exists and is reachable via `--provider imagen`, but Vertex AI authentication is out of scope for v0.3.0. If no Vertex token is available, the CLI will exit with a clear error pointing to `docs/IMAGEN_VERTEX_SETUP.md` (coming in v0.3.x).

- **Keychain service:** `pushing-creation:imagen`
- **Image model:** `imagegeneration@006` (Vertex AI)
- **Video:** Not supported. Use gemini provider for Veo video.
- **Auth:** GCP project ID + Vertex AI access token
- **Key format:** `project-id:ya29.XXXXXXXX` (colon-separated)
- **Where to get:** [cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai); enable the Vertex AI API in your GCP project
- **Quirk:** Access tokens expire after 1 hour. Refresh with `gcloud auth print-access-token`. For persistent use, a service account with Application Default Credentials is preferred.
