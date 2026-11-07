# THE DAWG AGENT 🐶

**An approval-gated dog-video production and Instagram workflow, built to be understandable and safe to extend.**

THE DAWG AGENT currently turns a supplied image into a short vertical MP4 preview. It also contains a database-backed post queue, an API, Cloudinary upload code, an Instagram publishing adapter, and a scheduler worker.

> **Project status:** Early development. AI image generation and automatic prompt generation are not connected. External publishing integrations require credentials and end-to-end verification. Publishing is OFF by default.

> **License:** This repository is source-available under a custom **Personal, Non-Commercial, Limited-Customization License**. You may use it privately and non-commercially, and may only configure the supported image-generation type, publishing type/provider, and asset type/source/format. No other code, prompt, workflow, or feature modifications are permitted. Redistribution and commercial use are prohibited without written permission. The copyright owner retains all commercial rights. See [LICENSE](LICENSE).

## Start here

New to the project? Follow the guides in this order:

1. **[Install and run the project](docs/START_HERE.md)** — Python, FFmpeg installation, PATH verification, virtual environment, dependencies, first preview.
2. [How the agent works](docs/HOW_IT_WORKS.md) — architecture, queue, API, worker, and current limitations.
3. [Add a post](docs/ADD_A_POST.md) — create JSON input and render a local preview.
4. [Customize prompts, post types, and audio](docs/CUSTOMIZE_PROMPTS.md) — creative guidance and honest feature status.
5. [Project map](docs/PROJECT_MAP.md) — where each component lives.
6. [Troubleshooting](docs/TROUBLESHOOTING.md) — common Windows, Python, FFmpeg, and API errors.

## Requirements

- Python 3.11+
- FFmpeg and FFprobe installed and available on PATH
- Windows 10/11, macOS, or Linux
- Git recommended

## Quick start

Follow the full [installation guide](docs/START_HERE.md). The short version:

```bash
git clone https://github.com/Moazzam-Siddiqui/THE_DAWG_AGENT.git
cd THE_DAWG_AGENT
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install the package:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Check FFmpeg before rendering:

```bash
ffmpeg -version
ffprobe -version
```

## What is implemented?

| Component | Current state |
|---|---|
| Local image-to-video rendering | Implemented; needs continued runtime testing |
| Video file validation | Basic checks implemented |
| Post queue and database | Implemented |
| FastAPI control API | Implemented |
| Cloudinary upload adapter | Code present; credentials and live upload not verified |
| Instagram Graph API adapter | Code present; credentials and live publishing not verified |
| Scheduler worker | Code present; scheduling/rate-limit hardening still required |
| AI prompt generation | Not connected |
| AI image generation | Not connected |
| Multi-track audio editing | Not implemented |
| Web dashboard | Not implemented |
| Deployment | Not configured |

## Safety defaults

- `PUBLISH_ENABLED=false`
- `REQUIRE_APPROVAL=true`
- Default daily publishing limit: 3
- Default minimum publishing interval: 180 minutes
- Default publishing window: 07:00–22:00 Asia/Kolkata

These are configuration defaults, not a claim that live publishing has been fully safety-tested. Keep publishing disabled until the integration and worker safeguards have been verified.

## Development checks

```bash
python -m pytest
```

## Security

- Keep secrets in your local `.env` file or a secure deployment secret store.
- Never commit `.env`, access tokens, API keys, or passwords.
- Do not expose the development API publicly.
- Do not enable live publishing until the safety checks are complete.

## License

This project is **not open source**. It is source-available for personal, non-commercial use with only three permitted customization categories: selecting/configuring a supported image-generation type, publishing type/provider, and asset type/source/format. All other modifications—including source-code, prompt, workflow, logic, and feature changes—are prohibited without prior written permission. Redistribution, sharing, resale, and commercial use are also prohibited. The owner reserves all commercial rights. Read the full [LICENSE](LICENSE) before using it.
