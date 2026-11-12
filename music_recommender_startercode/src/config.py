import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GEMINI_MODEL = "gemini-3.5-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
SETLISTFM_API_KEY = os.getenv("SETLISTFM_API_KEY")


def require(name):
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing {name}. Copy .env.example to .env and fill it in.")
    return v
