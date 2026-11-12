"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys

from src.recommender import load_songs, recommend_songs

# Taste profile: someone studying or coding late at night. Keys match the
# column names in data/songs.csv so score_song can compare them directly.
LATE_NIGHT_FOCUS = {
    # Categorical: exact-match preferences
    "genre": "lofi",
    "mood": "focused",
    # Numeric 0-1 targets: the ideal value for each feature
    "energy": 0.40,            # calm, not sleepy
    "valence": 0.58,           # emotionally neutral
    "danceability": 0.60,      # steady beat, not made for dancing
    "acousticness": 0.75,      # warm, organic textures
    "speechiness": 0.04,       # lyrics would be distracting
    "instrumentalness": 0.85,  # mostly or entirely instrumental
    # Numeric, other scales: normalize before comparing
    "tempo_bpm": 80,           # slow, unhurried pulse
    "popularity": 55,          # 0-100; neither chart-topping nor obscure
    "duration_sec": 190,       # short loops that are easy to leave on repeat
}

# Contrast profile: high-energy, vocal-heavy, fully produced. It sits opposite
# LATE_NIGHT_FOCUS on energy, acousticness, speechiness and instrumentalness.
HIP_HOP_HEAD = {
    "genre": "hip hop",
    "mood": "confident",
    "energy": 0.80,
    "valence": 0.58,
    "danceability": 0.85,
    "acousticness": 0.08,
    "speechiness": 0.30,
    "instrumentalness": 0.0,
    "tempo_bpm": 92,
    "popularity": 80,
    "duration_sec": 215,
}


# Upbeat mainstream profile: bright, danceable, popular, vocal-forward.
POP_HAPPY = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.80,
    "valence": 0.85,
    "danceability": 0.80,
    "acousticness": 0.20,
    "speechiness": 0.08,
    "instrumentalness": 0.0,
    "tempo_bpm": 118,
    "popularity": 85,
    "duration_sec": 200,
}

# Pick one from the command line: python3 -m src.main pop_happy
PROFILES = {
    "late_night_focus": LATE_NIGHT_FOCUS,
    "hip_hop_head": HIP_HOP_HEAD,
    "pop_happy": POP_HAPPY,
}

WIDTH = 60
BAR_LEN = 20


def format_recommendation(rank: int, song: dict, score: float, explanation: str) -> str:
    """Renders one recommendation as a small card: title, score bar, reasons."""
    filled = round(score * BAR_LEN)
    bar = "█" * filled + "░" * (BAR_LEN - filled)
    lines = [
        "─" * WIDTH,
        f"#{rank}  {song['title']}",
        f"    {song['artist']} · {song['genre']} · {song['mood']}",
        f"    Score: {score:.2f} / 1.00  {bar}",
        "    Why:",
    ]
    lines += [f"      • {reason}" for reason in explanation.split("; ")]
    return "\n".join(lines)


def main() -> None:
    """Loads the songs, scores them for the chosen profile, and prints the top 5."""
    songs = load_songs("data/songs.csv")

    name = sys.argv[1] if len(sys.argv) > 1 else "late_night_focus"
    if name not in PROFILES:
        sys.exit(f"Unknown profile '{name}'. Choose from: {', '.join(PROFILES)}")
    user_prefs = PROFILES[name]

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("=" * WIDTH)
    print(f"TOP {len(recommendations)} RECOMMENDATIONS  ({len(songs)} songs scanned)")
    print(f"Profile: {user_prefs['genre']} / {user_prefs['mood']}")
    print("=" * WIDTH)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(format_recommendation(rank, song, score, explanation))
    print("─" * WIDTH)


if __name__ == "__main__":
    main()
