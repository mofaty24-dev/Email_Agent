# Email Assistant

A LangChain/LangGraph agent that lets you search and send Gmail messages through a chat interface. The user must authenticate first, and every outgoing email requires explicit human approval before it is sent.

## What's New

This version replaces the original local-Ollama email summarizer (`email_agent.py` + `email_extractor.py`) with a single tool-calling agent in `Email_Assistant.py`.

| Area | Before | Now |
|------|--------|-----|
| Entry point | `email_agent.py` / `email_extractor.py` | `Email_Assistant.py` (exports `agent`) |
| Capability | Summarize the latest 3 emails | Search the inbox, send emails, authenticate users |
| LLM | Local Ollama (`gemma2:9b`) | Groq-hosted model via `models.py` (`groq_model`) |
| Email access | `imap-tools` | Standard-library `imaplib` (read) and `smtplib` (send) |
| Interaction | One-shot script | Conversational agent served by LangGraph (`langgraph dev`) |
| Safety | Read-only | Authentication gate + human-in-the-loop approval for sending |

### Agent design

- **Tools**
  - `authenticate(email, password)` checks the credentials against the `Email_Context` defaults and sets `authenticated` in the agent state.
  - `search_emails(sender, subject, since, unread, limit)` searches the Gmail inbox over IMAP (read-only, `BODY.PEEK` so messages are not marked as read) and returns id, sender, subject and date. `since` uses the `DD-Mon-YYYY` format, e.g. `01-Oct-2026`.
  - `send_email(to_email, subject, body)` sends a plain-text email through `smtp.gmail.com:587` (STARTTLS).
- **Middleware**
  - `dynamic_tool_call` exposes only `authenticate` until the user is authenticated, then `search_emails` and `send_email`.
  - `dynamic_prompt_func` switches the system prompt based on the authentication state.
  - `HumanInTheLoopMiddleware` pauses before `send_email` for approval; `authenticate` and `search_emails` run without interruption.
- **State and context**: `AuthenticationState` extends `AgentState` with an `authenticated` flag; `Email_Context` carries the credentials used by `authenticate`.

### Added project files

| File | Purpose |
|------|---------|
| `Email_Assistant.py` | The agent (tools, middleware, `agent` graph) |
| `models.py` | Defines `groq_model` (`ChatGroq`, `llama-3.3-70b-versatile`) |
| `langgraph.json` | Registers the graph `email_assistant` -> `./Email_Assistant.py:agent` for LangGraph |
| `package.json` | Provides the `pnpm dev` script |
| `pyproject.toml` | Python dependencies |
| `.env.example` | Template for required environment variables |
| `.gitignore` | Keeps `.env`, virtualenvs and caches out of git |

## Prerequisites

- Python 3.11+ and [uv](https://github.com/astral-sh/uv)
- Node.js and [pnpm](https://pnpm.io/) (only needed for `pnpm dev`)
- A Gmail account with IMAP enabled and an **app password** (requires 2-Step Verification)
- A [Groq](https://console.groq.com/) API key

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/mofaty24-dev/Email_Agent.git
   cd Email_Agent
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment variables**

   Copy the template and fill in your values:
   ```bash
   cp .env.example .env
   ```
   ```env
   EMAIL_ADDRESS=youraddress@gmail.com
   EMAIL_PASSCODE=your16charapppassword
   GROQ_API_KEY=your_groq_api_key
   ```

   > Never commit `.env`. It is listed in `.gitignore`.

## Launching

Both options start the LangGraph dev server (default `http://127.0.0.1:2024`) and open LangGraph Studio, where you can chat with the `email_assistant` graph.

**Option 1: `pnpm dev`**
```bash
pnpm dev
```
This runs `uv run langgraph dev` (see `package.json`). There are no Node dependencies to install.

**Option 2: `langgraph dev`**
```bash
uv run langgraph dev
```
Or, with the virtual environment activated:
```bash
source .venv/bin/activate      # Windows: .venv\Scripts\activate
langgraph dev
```

## Usage

1. Open the Studio URL printed in the terminal and select the `email_assistant` graph.
2. Authenticate when the assistant asks for your email and password.
3. Ask it to search your inbox, for example: "Show my unread emails from the last week".
4. Ask it to send an email. The run pauses so you can approve, edit or reject the message before anything is sent.

## Configuration

| Variable | Description |
|----------|-------------|
| `EMAIL_ADDRESS` | Gmail address used for IMAP search and SMTP sending |
| `EMAIL_PASSCODE` | Gmail app password (not your login password) |
| `GROQ_API_KEY` | API key for the Groq-hosted model |

To change the model, edit `models.py`.

## Project Structure

```
.
├── Email_Assistant.py   # Agent: tools, middleware, graph
├── models.py            # LLM definition (groq_model)
├── langgraph.json       # LangGraph graph registration
├── package.json         # `pnpm dev` launcher
├── pyproject.toml       # Python dependencies
├── .env.example         # Environment variable template
└── README.md
```

## Security Notes

- Use a Gmail app password, never your main account password.
- Sending email always requires human approval.
- Inbox search is read-only.
- Email content and prompts are sent to Groq's API for inference.

## License

MIT
