---
description: Manage API keys for pushing-creation providers in macOS Keychain
argument-hint: "[add|list|test|remove] [provider]"
---

Manage provider API keys stored in macOS Keychain by running bin/frames-keys.

## Subcommands

Run bin/frames-keys with one of these subcommands based on what the user asks:

**frames-keys add <provider>**
Add or update a key. Runs an interactive prompt (hidden input). Use this when the user wants to add a new provider or update an existing key.

```
bin/frames-keys add gemini
```

**frames-keys list**
List all pushing-creation Keychain entries by service name. No values are shown.

```
bin/frames-keys list
```

**frames-keys test <provider>**
Make a live ping to verify the key works. Prints [ok] or [fail] with a scrubbed reason.

```
bin/frames-keys test gemini
```

**frames-keys remove <provider>**
Delete a key from Keychain.

```
bin/frames-keys remove gemini
```

## When the user just types /frames-keys

Show them this menu and ask what they want to do:
- add -- store a new provider key
- list -- see what keys are stored
- test <provider> -- verify a key works
- remove <provider> -- delete a key

Do NOT print or echo any key values. The CLI handles all scrubbing.
