# RyanGPT

A private chat app that talks the way Ryan runs a working conversation.

You bring an experiment, a plan, a plot, a table, or a hardware status. RyanGPT
answers as a stand-in that applies Ryan's review bar from the 9 Oct and 12 Oct
2026 lab meetings: it pushes the work as far as it can go before you show the
real Ryan. It is a single Python HTTP server plus one HTML page, a SQLite
database, and the OpenAI chat API. No framework, no build step, no dependencies
beyond the Python standard library.

It is being deployed on [Fly.io](https://fly.io) as the `ryangpt` app.

## What it does

- **Two message modes.** *Talk* is plain conversation — the objection, if there
  is one, then stop. *Report* is a colleague-facing writeup, and it follows the
  four-part standard (exact title and purpose, architecture, context behind the
  findings, and the author's own score or "not scored").
- **Threads.** Each conversation is a "meeting" stored in SQLite. You can create,
  rename, and delete them from the sidebar.
- **Image attachments.** Paste or attach an image and it becomes the artifact
  under review; images are stored and sent back to the model on later turns.
- **Durable notes.** Notes pinned in the sidebar are injected into every prompt
  as background context.
- **Model auto-pick.** The server probes the OpenAI key against a priority list
  (newest flagship first) and caches the winner. You can also pin a model.

The review behavior itself lives in `.cursor/skills/ryan-review/`
(`SKILL.md`, `expectations.md`, `examples.md`), which the server reads at
startup and folds into the system prompt. Edit those files to change how it
talks; no code change needed.

## Requirements

- Python 3.10 or newer (the Docker image uses 3.12).
- An OpenAI API key.

## Run it locally

1. **Clone the repo.**

   ```sh
   git clone https://github.com/4nddrs/LLM-Ryan.git
   cd LLM-Ryan
   ```

2. **Create the `.env` file at the repo root** with your OpenAI key:

   ```sh
   KEY_OPENAI=sk-your-key-here
   ```

   The server reads this file directly, so no shell export is needed.

3. **Start the server.**

   ```sh
   python3 chat/server.py
   ```

4. **Open** <http://127.0.0.1:8787>.

The first run creates `chat/ryan.db` (SQLite) and picks a model for your key.
The chosen model is cached in `chat/.model`. Both are git-ignored.

### Configuration

Every value has a working default. Set these as environment variables to
override them (environment variables win over `.env`).

| Variable        | Default              | Meaning                                              |
| --------------- | -------------------- | ---------------------------------------------------- |
| `KEY_OPENAI`    | — (required)         | OpenAI API key.                                      |
| `HOST`          | `127.0.0.1`          | Bind address. Use `0.0.0.0` to expose the server.    |
| `PORT`          | `8787`               | HTTP port.                                           |
| `DB_PATH`       | `chat/ryan.db`       | SQLite database path.                                |
| `MODEL`         | auto-detected        | Pin a model instead of probing the key.              |
| `APP_PASSWORD`  | unset (auth off)     | When set, the app is behind a password login screen. |

## Run with Docker

```sh
docker build -t ryangpt .
docker run --rm -p 8080:8080 \
  -e KEY_OPENAI=sk-your-key-here \
  -e APP_PASSWORD=choose-a-password \
  -v ryan_data:/data \
  ryangpt
```

Then open <http://127.0.0.1:8080>. The database is stored on the `ryan_data`
volume at `/data/ryan.db`.

## Deploy on Fly.io

The app ships with a `fly.toml` for the `ryangpt` Fly app: one machine in the
`ewr` region, a `ryan_data` volume mounted at `/data` for the SQLite database,
and machines that stop when idle and start on request.

One-time setup:

```sh
fly apps create ryangpt
fly volumes create ryan_data --region ewr --size 1 -a ryangpt
fly secrets set KEY_OPENAI=... APP_PASSWORD=... -a ryangpt
```

Deploy:

```sh
fly deploy -a ryangpt
```

`KEY_OPENAI` and `APP_PASSWORD` are set as Fly secrets, never committed to the
repo. On Fly the session cookie is marked `Secure` automatically, and the health
check hits `/api/meta`.

## Layout

```
chat/
  server.py     # HTTP server: API, SQLite, OpenAI streaming, login
  index.html    # the whole front end (vanilla JS, no build)
  ryan.db       # local SQLite database (git-ignored)
  .model        # cached model name (git-ignored)
.cursor/skills/ryan-review/   # the review rules loaded into the system prompt
Dockerfile                    # python:3.12-slim image
fly.toml                      # Fly.io app config
.env                          # KEY_OPENAI (git-ignored)
```

## Notes

- The app has no accounts. Local access is open by default; set
  `APP_PASSWORD` before exposing it anywhere, as the Fly deployment does.
- The database, cached model, and `.env` are all git-ignored — never commit
  your key or your chat history.
