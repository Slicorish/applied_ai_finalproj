import csv
# import heapq  # TODO: needed for the heapq.nlargest versions noted below
from operator import itemgetter
from typing import Dict, Iterable, Iterator, List, Tuple
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    speechiness: float = 0.0
    instrumentalness: float = 0.0
    popularity: int = 0
    duration_sec: int = 0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

# Strategy 3: weighted decision matrix. Weights sum to 1.0.
WEIGHTS: Dict[str, float] = {
    "genre": 0.20,
    "mood": 0.20,
    "energy": 0.15,
    "valence": 0.08,
    "acousticness": 0.07,
    "danceability": 0.04,
    "tempo_bpm": 0.04,
    "speechiness": 0.08,
    "instrumentalness": 0.07,
    "popularity": 0.04,
    "duration_sec": 0.03,
}

CATEGORICAL = ("genre", "mood")
# Features not on a 0-1 scale: the difference that scores 0.
FEATURE_RANGES = {
    "tempo_bpm": 100.0,
    "popularity": 100.0,
    "duration_sec": 300.0,
}

# Categories that are close enough to earn partial credit.
RELATED_MOODS = [
    {"chill", "relaxed", "peaceful", "focused"},
    {"intense", "angry", "aggressive", "defiant"},
    {"happy", "uplifting", "euphoric", "energetic"},
    {"sad", "melancholic", "nostalgic", "reflective"},
]
RELATED_GENRES = [
    {"pop", "indie pop"},
    {"hip hop", "r&b"},
    {"rock", "metal"},
    {"lofi", "ambient", "jazz"},
    {"edm", "synthwave"},
]
RELATED_CREDIT = 0.5


def _group_lookup(groups: List[set]) -> Dict[str, int]:
    """Maps each value to its group index so relatedness is an O(1) lookup."""
    return {value: i for i, group in enumerate(groups) for value in group}


CATEGORY_GROUPS = {
    "genre": _group_lookup(RELATED_GENRES),
    "mood": _group_lookup(RELATED_MOODS),
}


def _feature_score(feature: str, target, value) -> float:
    """Scores one feature from 0 to 1."""
    if feature in CATEGORICAL:
        if target == value:
            return 1.0
        groups = CATEGORY_GROUPS[feature]
        group = groups.get(target)
        return RELATED_CREDIT if group is not None and group == groups.get(value) else 0.0
    scale = FEATURE_RANGES.get(feature, 1.0)
    return max(0.0, 1.0 - abs(value - target) / scale)


def _active_weights(user_prefs: Dict) -> Dict[str, float]:
    """
    Weights for the features present in user_prefs, rescaled to sum to 1.
    Depends only on the profile, so compute it once per request.
    """
    active = {f: w for f, w in WEIGHTS.items() if f in user_prefs}
    total = sum(active.values())
    return {f: w / total for f, w in active.items()} if total else {}


def _score(user_prefs: Dict, weights: Dict[str, float], song: Dict) -> float:
    """Fast path: the score only, with no strings built."""
    return sum(
        weight * _feature_score(feature, user_prefs[feature], song[feature])
        for feature, weight in weights.items()
    )


def explain_song(user_prefs: Dict, weights: Dict[str, float], song: Dict) -> List[str]:
    """Builds the reasons behind a score. Run it only on songs worth showing."""
    reasons = []
    for feature, weight in weights.items():
        fit = _feature_score(feature, user_prefs[feature], song[feature])
        points = weight * fit
        if feature in CATEGORICAL:
            if fit == 1.0:
                reasons.append(f"{feature} match ({song[feature]}) +{points:.2f}")
            elif fit > 0:
                reasons.append(
                    f"{feature} related ({song[feature]} ~ {user_prefs[feature]}) +{points:.2f}"
                )
        elif fit >= 0.8:
            reasons.append(f"{feature} close to target +{points:.2f}")
    return reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Stores the song catalog to recommend from."""
        self.songs = songs

    @staticmethod
    def _prefs(user: UserProfile) -> Dict:
        """Converts a UserProfile into the prefs dict the scoring functions expect."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "acousticness": 0.8 if user.likes_acoustic else 0.2,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the k songs that best match the user's profile, best first."""
        prefs = self._prefs(user)
        weights = _active_weights(prefs)
        scored = [(_score(prefs, weights, vars(song)), song) for song in self.songs]
        scored.sort(key=itemgetter(0), reverse=True)
        # TODO (larger datasets): replace the list + sort above with a streaming
        # top-k, O(n log k) time and O(k) memory instead of O(n log n) and O(n):
        #   scored = ((_score(prefs, weights, vars(song)), song) for song in self.songs)
        #   return [song for _, song in heapq.nlargest(k, scored, key=itemgetter(0))]
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns the scoring reasons for a song as one "; "-separated string."""
        prefs = self._prefs(user)
        return "; ".join(explain_song(prefs, _active_weights(prefs), vars(song)))

def iter_songs(csv_path: str) -> Iterator[Dict]:
    """Lazily yields one typed song dict per CSV row."""
    int_fields = {"id", "tempo_bpm", "popularity", "duration_sec"}
    text_fields = {"title", "artist", "genre", "mood"}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            yield {
                key: value if key in text_fields
                else int(value) if key in int_fields
                else float(value)
                for key, value in row.items()
            }

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    return list(iter_songs(csv_path))

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Returns a score from 0 to 1 and the reasons behind it. Only features
    present in user_prefs count; weights are renormalized over those.
    """
    weights = _active_weights(user_prefs)
    return _score(user_prefs, weights, song), explain_song(user_prefs, weights, song)

def recommend_songs(user_prefs: Dict, songs: Iterable[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Scores every song, sorts, and keeps the top k. Explanations are built
    for those k alone.
    """
    weights = _active_weights(user_prefs)
    scored = [(_score(user_prefs, weights, song), song) for song in songs]
    scored.sort(key=itemgetter(0), reverse=True)
    top = scored[:k]

    # TODO (larger datasets): swap the list + sort above for heapq.nlargest.
    # It keeps only the k best while streaming, so it runs in O(n log k) time
    # and O(k) memory instead of O(n log n) and O(n). Pair it with the lazy
    # iter_songs() loader so the full catalog is never held in memory:
    #
    #   scored = ((_score(user_prefs, weights, song), song) for song in songs)
    #   top = heapq.nlargest(k, scored, key=itemgetter(0))
    #
    # Uncomment `import heapq` at the top of the file when you switch.
    # nlargest matches sorted(..., reverse=True)[:k], ties included.

    return [
        (song, score, "; ".join(explain_song(user_prefs, weights, song)) or "no strong matches")
        for score, song in top
    ]
