"""
Tests for the Phase 1 dataset pipeline.

Covers the pure helpers in scripts/build_songs_csv.py (mood derivation, artist
splitting, genre normalization) and checks that the generated data/songs.csv is
consistent with them and with the RELATED_GENRES / RELATED_MOODS groups used by
src/recommender.py.
"""

import csv
import importlib.util
from pathlib import Path

from src.recommender import CATEGORY_GROUPS, load_songs

ROOT = Path(__file__).resolve().parent.parent
SONGS_CSV = ROOT / "data" / "songs.csv"

_spec = importlib.util.spec_from_file_location("build_songs_csv", ROOT / "scripts" / "build_songs_csv.py")
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)


def test_derive_mood_covers_the_grid():
    """Checks derive_mood returns the expected label for cells across the 3x3 grid."""
    assert build.derive_mood(valence=0.9, energy=0.9) == "euphoric"
    assert build.derive_mood(valence=0.1, energy=0.9) == "aggressive"
    assert build.derive_mood(valence=0.5, energy=0.6) == "confident"
    assert build.derive_mood(valence=0.1, energy=0.2) == "sad"
    assert build.derive_mood(valence=0.5, energy=0.2) == "chill"


def test_split_artists_and_genre_normalization():
    """Checks artists split on ';' with blanks and case-insensitive repeats removed,
    and that Spotify genre slugs become plain names ('hip-hop' -> 'hip hop')."""
    assert build.split_artists("A;B; a ;C") == ["A", "B", "C"]
    assert build.normalize_genre("hip-hop") == "hip hop"
    assert build.normalize_genre("r-n-b") == "r&b"


def test_songs_csv_matches_derivation_rule_and_has_unique_ids():
    """Checks every row of data/songs.csv: ids are unique, `mood` equals what
    derive_mood gives for its valence/energy, and `artist` is the first entry
    of `all_artists`."""
    songs = load_songs(str(SONGS_CSV))
    assert len(songs) > 1000
    assert len({s["id"] for s in songs}) == len(songs)
    for s in songs:
        assert s["mood"] == build.derive_mood(s["valence"], s["energy"])
        assert s["artist"] == s["all_artists"].split("|")[0]


def test_related_values_exist_in_the_data():
    """Checks every genre and mood named in the related-credit groups actually
    occurs in songs.csv, so a typo or a renamed label can't silently earn no credit."""
    songs = load_songs(str(SONGS_CSV))
    for feature in ("genre", "mood"):
        present = {s[feature] for s in songs}
        assert set(CATEGORY_GROUPS[feature]) <= present
