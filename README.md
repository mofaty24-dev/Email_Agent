# Email Summarizer Agent

A lightweight AI agent that fetches your latest emails via IMAP and summarizes them using a local LLM (Ollama), without sending your data to any third-party API.

## Features

- Fetches the latest N emails from any IMAP-compatible provider (Gmail, Outlook, Yahoo, etc.)
- Summarizes email content locally using [Ollama](https://ollama.com/) — no data leaves your machine
- Strict summarization rules: no fabricated details, no dropped information
- Renders output as clean Markdown

## Tech Stack

- **Python 3.12** (managed via [uv](https://github.com/astral-sh/uv))
- **[imap-tools](https://pypi.org/project/imap-tools/)** — IMAP email fetching
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — environment variable management
- **[Ollama](https://ollama.com/)** — local LLM inference (default model: `gemma2:9b`)
- **IPython** — Markdown rendering of the summary

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) installed
- [Ollama](https://ollama.com/) installed and running locally, with the `gemma2:9b` model pulled:
  ```bash
  ollama pull gemma2:9b
  ```
- An email account with IMAP access enabled and an **app password** generated (Gmail requires 2-Step Verification to be enabled first)

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/mofaty24-dev/<repo-name>.git
   cd <repo-name>
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root (same level as `pyproject.toml`, **not** inside `.venv`):
   ```env
   EMAIL_ADDRESS=youraddress@gmail.com
   EMAIL_PASSCODE=your16charapppassword
   ```

   > **Note:** Never commit `.env` to version control. Ensure it's listed in `.gitignore`.

4. **Run the summarizer**
   ```bash
   uv run python summarizer.py
   ```

## How It Works

1. `email_extractor.py` connects to the configured IMAP server and fetches the latest emails (default: 3), combining sender, subject, date, and body into a single text block.
2. `summarizer.py` passes that text to a local Ollama model (`gemma2:9b`) with a system prompt instructing it to summarize faithfully — no invented details, no omitted points.
3. The summary is rendered as Markdown in the console/notebook output.

## Configuration

| Variable          | Description                                   |
|--------------------|------------------------------------------------|
| `EMAIL_ADDRESS`    | Your email address                             |
| `EMAIL_PASSCODE`   | App-specific password (not your login password)|

To fetch from a non-Gmail provider, update `IMAP_SERVER` in `email_extractor.py` (e.g. `outlook.office365.com` for Outlook).

To use a different local model, change the `model` parameter in `summarizer.py`'s `chat()` call to any model available in your local Ollama installation.

## Project Structure

```
.
├── email_extractor.py   # IMAP fetching logic
├── summarizer.py         # LLM summarization and display logic
├── pyproject.toml        # Project dependencies (managed by uv)
├── .env                  # Local credentials (not committed)
└── README.md
```

## Known Issues

- `email_fetch()` currently builds the message list but does not return the combined text — this needs a return statement combining sender/subject/date/body into a single string before this pipeline will run end-to-end.

## Security Notes

- Uses IMAP app passwords rather than your main account password
- All LLM processing happens locally via Ollama — no email content is sent to external APIs
- Only fetches emails (read-only `AND(all=True)` filter) — does not send, delete, or modify anything

## License

MIT
