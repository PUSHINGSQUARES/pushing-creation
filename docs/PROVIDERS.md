# Providers

pushing-creation supports direct generation through these providers.

## Verification matrix

| Provider | Image | Video | Verified | Notes |
|----------|-------|-------|----------|-------|
| gemini | yes | yes | scaffolded | Gemini Flash image + Veo 2 video via Google AI Studio |
| openai | yes | no | scaffolded | GPT-image-1; no video support |
| openrouter | yes | no | scaffolded | Pass-through to Flux 1.1 Pro and others |
| kling | no | yes | scaffolded | Kling v2 Master video; no image support |
| seedream | yes | no | scaffolded | Bytedance Seedream v3 via Volcano Engine |
| seedance | no | yes | scaffolded | Bytedance Seedance v1 Lite via Volcano Engine |
| imagen | yes | no | scaffolded | Google Imagen 006 via Vertex AI |

*Verification status will be updated after real-test gate runs with live Keychain entries.*

## Provider details

### Gemini

- **Keychain service:** `pushing-creation:gemini`
- **Image model:** `gemini-2.0-flash-preview-image-generation`
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
- **Auth:** Kling API bearer token
- **Where to get:** [klingai.com](https://klingai.com) under API settings
- **Quirk:** Generation is async; CLI polls until complete (up to 10 minutes)

### Seedream

- **Keychain service:** `pushing-creation:seedream`
- **Image model:** `seedream-v3`
- **Video:** Not supported. Use seedance for video.
- **Auth:** Volcano Engine `access_key:secret_key` (HMAC-SHA256 signed)
- **Key format:** Store as `AKXXXXXXXX:secretXXXXXX` (colon-separated)
- **Where to get:** [console.volcengine.com](https://console.volcengine.com) under Access Control
- **Quirk:** Bytedance request signing requires timestamp-based HMAC. Key is two parts separated by colon.

### Seedance

- **Keychain service:** `pushing-creation:seedance`
- **Video model:** `seedance-v1-lite`
- **Image:** Not supported. Use seedream for images.
- **Auth:** Same Volcano Engine `access_key:secret_key` as Seedream
- **Key format:** `AKXXXXXXXX:secretXXXXXX`
- **Where to get:** [console.volcengine.com](https://console.volcengine.com)
- **Quirk:** Same HMAC signing as Seedream. Same credentials can be used if your account has both services enabled.

### Imagen

- **Keychain service:** `pushing-creation:imagen`
- **Image model:** `imagegeneration@006` (Vertex AI)
- **Video:** Not supported. Use gemini provider for Veo video.
- **Auth:** GCP project ID + Vertex AI access token
- **Key format:** `project-id:ya29.XXXXXXXX` (colon-separated)
- **Where to get:** [cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai); enable the Vertex AI API in your GCP project
- **Quirk:** Access tokens expire after 1 hour. Refresh with `gcloud auth print-access-token`. For persistent use, a service account with Application Default Credentials is preferred.
