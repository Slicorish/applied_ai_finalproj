"""
Builds data/songs.csv from the Kaggle "Spotify Tracks Dataset"
(maharshipandya/spotify-tracks-dataset, ~114k rows, license: BSD).

Get the raw file (Kaggle, or the identical Hugging Face mirror) and save it as
data/raw/dataset.csv, which is git-ignored:

    curl -L -o data/raw/dataset.csv \
      https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset/resolve/main/dataset.csv

Then, from music_recommender_startercode/:

    python3 scripts/build_songs_csv.py [--raw data/raw/dataset.csv] [--out data/songs.csv]

Pipeline (deterministic, stdlib only):
  1. Drop rows with a missing title/artist, or tempo/duration of 0, and
     the genres in DROP_GENRES.
  2. Normalize genre names: "hip-hop" -> "hip hop", "r-n-b" -> "r&b", ...
  3. Split the multi-artist field ("A;B;C"): `artist` is the primary (first)
     artist, `all_artists` keeps everyone joined by "|".
  4. Deduplicate: one row per track_id, then one per (title, primary artist).
     Where a track is listed under several genres, the most popular listing wins.
  5. Subsample: keep tracks with popularity >= MIN_POPULARITY, at most
     MAX_PER_ARTIST per artist, at most MAX_PER_GENRE per genre, best first.
     Popularity is the proxy for "popular and touring" artists until the
     Ticketmaster lookup is available.
  6. Derive `mood` from valence and energy (see derive_mood).
"""

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MIN_POPULARITY = 40
MAX_PER_ARTIST = 3
MAX_PER_GENRE = 30
# Non-music, plus playlist-style "genres" that are really moods and would
# collide with the derived `mood` values.
DROP_GENRES = {
    "comedy", "kids", "children", "disney",
    "happy", "sad", "chill", "party", "romance",
}
GENRE_RENAMES = {"r-n-b": "r&b", "rock-n-roll": "rock n roll", "j-pop": "j pop"}

FIELDS = [
    "id", "title", "artist", "all_artists", "genre", "mood", "energy",
    "tempo_bpm", "valence", "danceability", "acousticness", "speechiness",
    "instrumentalness", "popularity", "duration_sec",
]

# Mood rule: a 3x3 grid over energy (rows) and valence (columns), a simple
# version of the valence/arousal model of emotion. Cut points sit near the
# terciles of popular tracks so every cell gets songs.
#
#                 valence < 0.35   0.35 - 0.60    >= 0.60
#  energy >= 0.75   aggressive      energetic      euphoric
#  0.50 - 0.75      melancholic     confident      happy
#  energy < 0.50    sad             chill          relaxed
ENERGY_CUTS = (0.50, 0.75)
VALENCE_CUTS = (0.35, 0.60)
MOOD_GRID = [  # indexed [energy band][valence band], low to high
    ["sad", "chill", "relaxed"],
    ["melancholic", "confident", "happy"],
    ["aggressive", "energetic", "euphoric"],
]


def _band(value: float, cuts) -> int:
    """
    Buckets a 0-1 value into a band index using two cut points.

    Returns 0 below the first cut, 1 between the cuts, 2 at or above the second.
    """
    return sum(value >= c for c in cuts)


def derive_mood(valence: float, energy: float) -> str:
    """
    Maps valence and energy (both 0-1) to one of nine mood labels.

    Each value is bucketed with _band (ENERGY_CUTS / VALENCE_CUTS) and the two
    bands index MOOD_GRID, e.g. high energy + low valence -> "aggressive".
    """
    return MOOD_GRID[_band(energy, ENERGY_CUTS)][_band(valence, VALENCE_CUTS)]


def normalize_genre(raw: str) -> str:
    """
    Converts a raw Spotify genre slug into the project's genre name.

    Lowercases, applies GENRE_RENAMES for special cases ("r-n-b" -> "r&b"),
    and otherwise replaces hyphens with spaces ("hip-hop" -> "hip hop").
    """
    raw = raw.strip().lower()
    return GENRE_RENAMES.get(raw, raw.replace("-", " "))


def split_artists(raw: str) -> list:
    """
    Splits the raw multi-artist field "A;B;C" into ['A', 'B', 'C'].

    Trims whitespace and drops blanks and case-insensitive repeats, keeping the
    original order so the first name is the primary artist.
    """
    seen, artists = set(), []
    for name in (a.strip() for a in raw.split(";")):
        if name and name.lower() not in seen:
            seen.add(name.lower())
            artists.append(name)
    return artists


def _key(text: str) -> str:
    """Normalizes text for duplicate detection: collapses whitespace, trims, lowercases."""
    return re.sub(r"\s+", " ", text).strip().lower()


def read_clean(raw_path: Path) -> list:
    """Reads the raw CSV into cleaned dicts, applying steps 1-3."""
    out = []
    with open(raw_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            artists = split_artists(row["artists"])
            title = row["track_name"].strip()
            genre = normalize_genre(row["track_genre"])
            tempo = float(row["tempo"])
            duration = round(int(row["duration_ms"]) / 1000)
            if not artists or not title or tempo <= 0 or duration <= 0:
                continue
            if genre in DROP_GENRES:
                continue
            energy, valence = float(row["energy"]), float(row["valence"])
            out.append({
                "track_id": row["track_id"],
                "title": title,
                "artist": artists[0],
                "all_artists": "|".join(artists),
                "genre": genre,
                "mood": derive_mood(valence, energy),
                "energy": energy,
                "tempo_bpm": round(tempo),
                "valence": valence,
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "speechiness": float(row["speechiness"]),
                "instrumentalness": float(row["instrumentalness"]),
                "popularity": int(row["popularity"]),
                "duration_sec": duration,
            })
    return out


def subsample(rows: list) -> list:
    """Steps 4-5: dedupe, then pick the most popular tracks under the caps."""
    # Most popular first; ties break on title/id so the output is deterministic.
    rows = sorted(rows, key=lambda r: (-r["popularity"], r["title"], r["track_id"]))
    seen_ids, seen_songs = set(), set()
    per_artist, per_genre = Counter(), Counter()
    kept = []
    for r in rows:
        if r["popularity"] < MIN_POPULARITY:
            break  # sorted, so everything after is lower
        song_key = (_key(r["title"]), _key(r["artist"]))
        if r["track_id"] in seen_ids or song_key in seen_songs:
            continue
        artist_key = _key(r["artist"])
        if per_artist[artist_key] >= MAX_PER_ARTIST or per_genre[r["genre"]] >= MAX_PER_GENRE:
            continue
        seen_ids.add(r["track_id"])
        seen_songs.add(song_key)
        per_artist[artist_key] += 1
        per_genre[r["genre"]] += 1
        kept.append(r)
    return kept


def write_songs(rows: list, out_path: Path) -> None:
    """Writes the final CSV with sequential ids, grouped by genre."""
    rows = sorted(rows, key=lambda r: (r["genre"], -r["popularity"], r["title"]))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(rows, start=1):
            w.writerow({**r, "id": i})


def main() -> None:
    """Command-line entry point: reads the raw CSV, cleans and subsamples it,
    writes the songs CSV, and prints a summary of genres, artists and moods."""
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--raw", type=Path, default=ROOT / "data/raw/dataset.csv")
    p.add_argument("--out", type=Path, default=ROOT / "data/songs.csv")
    args = p.parse_args()

    cleaned = read_clean(args.raw)
    songs = subsample(cleaned)
    write_songs(songs, args.out)

    genres = Counter(s["genre"] for s in songs)
    moods = Counter(s["mood"] for s in songs)
    multi = sum("|" in s["all_artists"] for s in songs)
    print(f"{len(cleaned)} cleaned rows -> {len(songs)} songs -> {args.out}")
    print(f"{len(genres)} genres, {len({s['artist'] for s in songs})} primary artists, "
          f"{multi} multi-artist songs")
    print("moods:", dict(moods.most_common()))


if __name__ == "__main__":
    main()
