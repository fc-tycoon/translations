# FC Tycoon — Translations

This folder contains the community translation files for **FC Tycoon: Club Manager**.

If you want to help translate the game UI, you’re in the right place.

## What you need (Windows)

1. **Git** (to download/upload changes)
   - Download: https://git-scm.com/downloads

2. **Node.js (LTS)** (to run the validator)
   - Download: https://nodejs.org/
   - Install the **LTS** version

Optional (if you want to use the Python validator):

3. **Python 3.11+**
   - Download: https://www.python.org/downloads/

## Quick start (non-technical)

1. Download / clone the translations repo.
2. Double‑click **validate.cmd** to check that all YAML files are valid.
3. Edit translation files.
4. Double‑click **validate.cmd** again.
5. Commit + push (or open a pull request).

## Editing translations

Translations live under language folders:

- `en/` English (source language)
- `de/` German
- `es/` Spanish
- `fr/` French
- `jp/` Japanese
- `ko/` Korean
- `nl/` Dutch
- `pl/` Polish
- `pt/` Portuguese
- `zh/` Chinese (Simplified)

Each language folder contains several `.yaml` files (for example `ui.yaml`, `inbox.yaml`, `new_game_wizard.yaml`).

### Important YAML rules (common mistakes)

YAML is sensitive. Two common cases MUST be quoted:

1) Any value containing **colon + space** (`: `)

Bad:

```yaml
loaded_most_recent_save: Loaded most recent save: {name}
```

Good:

```yaml
loaded_most_recent_save: 'Loaded most recent save: {name}'
```

2) Any value that starts with `{...}` (placeholders)

Bad:

```yaml
save_success: {filename}.db saved
```

Good:

```yaml
save_success: '{filename}.db saved'
```

### Placeholders

Some translations include placeholders like `{name}`, `{count}`, `{filename}`.

- Keep the placeholder **exactly as-is**.
- You can move it around within the sentence.

## Validation

### Option A (recommended): Node validator

* After installing Node JS and cloning the repo.

From a terminal in this folder:

```bash
npm install
npm run validate
```

### Option B: Python validator

```bash
python -m pip install -r requirements.txt
python validate-yaml.py
```

## Submitting your changes

- If you have Git experience: commit to a branch and open a PR.
- If you don’t: you can still share a `.zip` of your changes with the team, but PRs are preferred.

Thanks for helping translate FC Tycoon.
