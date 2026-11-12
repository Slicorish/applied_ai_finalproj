# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Running Log: AI Suggestions (Accepted / Rejected / Revised)

| # | Phase | AI suggestion | Decision | Reason |
|---|-------|---------------|----------|--------|
| 1 | 0 | Use the `google-genai` SDK for Gemini | Accepted | It is the current SDK; installed 3.2.0 and a test call worked |
| 2 | 0 | Spotify Redirect URI `http://127.0.0.1:8888/callback`, with only **Web API** checked | Accepted | Spotify rejects `localhost`; the project only needs search, not playback or mobile SDKs |
| 3 | 0 | Spotify test snippet using `SpotifyClientCredentials()` with no arguments | Revised | It reads `SPOTIPY_*` env vars, but `.env` uses `SPOTIFY_*`, and it doesn't load `.env`. Changed to pass `client_id`/`client_secret` explicitly after `load_dotenv(".env")` |
| 4 | 0 | Test Gemini with `gemini-2.5-flash` / `gemini-2.0-flash` | Rejected | Both returned 404 (retired). Listed available models and switched to `gemini-3.5-flash`, which returned `ok` |
| 5 | 0 | Error message suggested `gemini-3.8-flash` | Rejected | It was not in my account's model list; used `gemini-3.5-flash` instead |
| 6 | 0 | Sketch of `config.py` with a `# ...etc` placeholder | Revised | Review found a trailing comma making `GEMINI_MODEL` a tuple, and only 2 of 6 keys loaded. Fixed the comma, loaded all keys, and anchored `load_dotenv` to the project's `.env` path |
| 7 | 0 | Move `.env` into the project folder and add `.env` / `.cache` to `.gitignore` | Accepted | `.env` was in the outer repo and not ignored, so keys could have been committed. Verified with `git check-ignore` |
| 8 | 0 | Develop Ticketmaster against mock data (`get_events(artist)`) while the key is pending | Accepted | Approval is outside my control; the mock lets other phases proceed |
| 9 | 0 | Use tickets.dev instead of the official Ticketmaster portal | Rejected (AI advised against) | Unverified third-party site; the official portal is developer.ticketmaster.com and issues the real key |
| 10 | 0 | Spotify search call as the Phase 0 check | Blocked | Credentials are valid but the API returned 403: the app owner needs an active Premium subscription. Paused; decide on Premium vs. Kaggle-only data |
| 11 | 0 | Put a separate Gemini key in this project instead of reusing an old one | Accepted | Separate keys can be revoked independently and don't share quota |
| 12 | 0 | setlist.fm test call that "timed out" | Diagnosed | Not an API problem: `curl` returned 200 in 0.4s. Slow `.venv` file loads made `import requests` take ~2 min. Second run: 200 in 1.3s |

**Still open:** Spotify (needs Premium owner) and Ticketmaster (key pending approval). Later phases will link to `logs/agent_traces.md`.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
