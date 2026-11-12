# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify's and YouTube's run a multi-stage pipeline: collaborative filtering and embedding millions of songs to a few hundred,which is a learned ranking model that predicts engagement (plays, skips, saves), with a final stage that adds diversity and context. Their weights are learned from huge amounts of user behavior, so they adapt over time and can surface unexpected picks. My algorithm is a content-based baseline. It scores each song by how close its energy, valence, mood and other attributes are to the user's stated preferences, using hand-picked weights, and then ranks the scores. That makes it fully explainable, but it ignores popularity, context, and other users' behavior. 

Written for: your README, for classmates and graders reading about your project.

---

This recommender is a content-based system that suggests songs by comparing each song's attributes to a user's stated taste profile. Each song is described by its genre, mood, energy, valence, acousticness, danceability and tempo, and the user profile stores a favorite genre, a favorite mood, and a target value for each numeric feature. To score a song, the system measures how close each numeric feature is to the user's target using `1 − |song value − target value|`. This rewards songs that match the user's preference rather than songs that simply have higher or lower values. Genre and mood each earn full credit for a match and none otherwise. These results are combined in a weighted sum, with energy (0.30) and valence (0.25) weighted most heavily because they are the two most independent audio dimensions in the dataset, followed by mood (0.20), acousticness (0.10), and genre, danceability and tempo (0.05 each). The weights add up to 1, so every song gets a score between 0 and 1. To make a recommendation, the system scores every song in the catalog, sorts them from highest to lowest, and returns the top *k* along with a short explanation of which features drove each score. Because the weights are hand-chosen and the system uses only song attributes, it is transparent and works for brand-new songs, but it can't learn from listening behavior, account for popularity or context, or add variety the way large-scale streaming recommenders do.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

Each Song in my system has ten fields, but only seven of them go into the score. The id, title and artist are used only to display results. Genre and mood are categorical features, scored as a match or no match. Energy, valence, acousticness, danceability and tempo are numeric features, scored by how close they are to the user's target. Tempo is first rescaled to a 0–1 range with (bpm − 60) / 92. Energy and valence matter most because they are the two mostly independent audio axes in the data, and together they carry 55% of the score.

The UserProfile currently stores a favorite genre, a favorite mood, a target energy and a boolean for whether the user likes acoustic music. That isn't enough for the scoring rule, which needs a target for every scored feature. I would expand it to add target valence, target danceability and target tempo, and replace the acoustic boolean with a target acousticness value. The profile holds stated preferences only, so it doesn't learn from skips or replays.

The Recommender scores each song by comparing it to the profile. For every numeric feature it computes closeness as 1 − |song value − target value|, so a song scores best when it sits near the user's target rather than when its value is high or low. For genre and mood it awards a 1 for a match and a 0 otherwise. The final score is the weighted sum of these results: energy 0.30, valence 0.25, mood 0.20, acousticness 0.10, and genre, danceability and tempo 0.05 each. The weights add up to 1, so every score falls between 0 and 1. The scoring function also returns short reasons, such as "energy within 0.02 of target", which feed the explanation shown with each recommendation.

To choose which songs to recommend, the system runs the scoring rule on every song in the catalog, sorts the songs from highest to lowest score, and returns the top k (five by default) along with their scores and explanations. Extra rules, such as excluding songs the user has already heard or penalizing repeated artists, would also go into this ranking step.

### Additions Beyond the Original Recipe

The recipe above was my original design. After writing it, I chose to extend the system with four more song features that the recipe did not include: `speechiness`, `instrumentalness`, `popularity` and `duration_sec`. I added them to `data/songs.csv`, to the `Song` class, and to the scoring in `src/recommender.py`, and both taste profiles in `src/main.py` set a target for each one. These additions were my own decision and go beyond the starter recipe, so the weights and descriptions in the paragraphs above are out of date for the current code.

- `speechiness` (0–1) captures how much of a track is spoken word, which helps separate hip hop from other genres.
- `instrumentalness` (0–1) captures how little vocal content a track has, which separates lofi, ambient and classical from vocal music.
- `popularity` (0–100) lets a profile prefer mainstream or niche songs.
- `duration_sec` lets a profile prefer shorter or longer tracks.

Adding them meant rebalancing the weights. The current values, which still sum to 1, are genre 0.20, mood 0.20, energy 0.15, valence 0.08, speechiness 0.08, acousticness 0.07, instrumentalness 0.07, danceability 0.04, tempo 0.04, popularity 0.04 and duration 0.03. Because tempo, popularity and duration are not on a 0–1 scale, their difference from the target is divided by a fixed range (100 BPM, 100 points and 300 seconds) before being turned into a closeness score.

---

## Documented Biases (as of Step 2)
The system has several potential biases that come from its dataset and its design. The 10-song dataset is imbalanced: lofi and pop have several songs, while most genres and moods appear only once, so users who like common genres get more matches than users who like rare ones. The dataset also has no classical, hip-hop, country, metal or non-English music, no songs that are both low in energy and low in valence, and a narrow valence range (0.48–0.84), so some tastes have no good match and the system will still return a confident-looking result. Two artists appear twice, and without a diversity rule one artist could dominate the top results. With so few songs, rankings below the top few are mostly noise. The design adds its own biases. Moods and genres are a fixed vocabulary chosen by the dataset's creator and are scored as exact matches, so near-matches like "relaxed" and "chill" get no credit. Energy and valence carry 55% of the score, which pulls every user's results toward one emotional region and under-serves listeners whose taste depends on lyrics, instruments or era. These features also reflect Western pop conventions and may describe other musical traditions poorly. Scoring by closeness to a single target point means a user who likes both very calm and very intense music is matched poorly to both. The weights are hand-picked and unvalidated, and the profile captures only what users say they like, not what they actually listen to. The main mitigations are to add more songs from underrepresented genres and moods, give partial credit to related moods and genres, penalize repeated artists, and test a profile for every genre and mood to confirm whether users with rare tastes receive consistently lower top scores.

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

TOP 5 RECOMMENDATIONS  (23 songs scanned)
Profile: lofi / focused
============================================================
────────────────────────────────────────────────────────────
#1  Focus Flow
    LoRoom · lofi · focused
    Score: 0.99 / 1.00  ████████████████████
    Why:
      • genre match (lofi) +0.20
      • mood match (focused) +0.20
      • energy close to target +0.15
      • valence close to target +0.08
      • acousticness close to target +0.07
      • danceability close to target +0.04
      • tempo_bpm close to target +0.04
      • speechiness close to target +0.08
      • instrumentalness close to target +0.07
      • popularity close to target +0.04
      • duration_sec close to target +0.03
────────────────────────────────────────────────────────────
#2  Midnight Coding
    LoRoom · lofi · chill
    Score: 0.88 / 1.00  ██████████████████░░
    Why:
      • genre match (lofi) +0.20
      • mood related (chill ~ focused) +0.10
      • energy close to target +0.15
      • valence close to target +0.08
      • acousticness close to target +0.07
      • danceability close to target +0.04
      • tempo_bpm close to target +0.04
      • speechiness close to target +0.08
      • instrumentalness close to target +0.07
      • popularity close to target +0.04
      • duration_sec close to target +0.03
────────────────────────────────────────────────────────────
#3  Library Rain
    Paper Lanterns · lofi · chill
    Score: 0.87 / 1.00  █████████████████░░░
    Why:
      • genre match (lofi) +0.20
      • mood related (chill ~ focused) +0.10
      • energy close to target +0.14
      • valence close to target +0.08
      • acousticness close to target +0.06
      • danceability close to target +0.04
      • tempo_bpm close to target +0.04
      • speechiness close to target +0.08
      • instrumentalness close to target +0.07
      • popularity close to target +0.04
      • duration_sec close to target +0.03
────────────────────────────────────────────────────────────
#4  Coffee Shop Stories
    Slow Stereo · jazz · relaxed
    Score: 0.76 / 1.00  ███████████████░░░░░
    Why:
      • genre related (jazz ~ lofi) +0.10
      • mood related (relaxed ~ focused) +0.10
      • energy close to target +0.15
      • valence close to target +0.07
      • acousticness close to target +0.06
      • danceability close to target +0.04
      • tempo_bpm close to target +0.04
      • speechiness close to target +0.08
      • instrumentalness close to target +0.07
      • popularity close to target +0.04
────────────────────────────────────────────────────────────
#5  Spacewalk Thoughts
    Orbit Bloom · ambient · chill
    Score: 0.72 / 1.00  ██████████████░░░░░░
    Why:
      • genre related (ambient ~ lofi) +0.10
      • mood related (chill ~ focused) +0.10
      • energy close to target +0.13
      • valence close to target +0.07
      • acousticness close to target +0.06
      • danceability close to target +0.03
      • tempo_bpm close to target +0.03
      • speechiness close to target +0.08
      • instrumentalness close to target +0.06
      • popularity close to target +0.03
────────────────────────────────────────────────────────────

---

## Experiments You Tried

 The weights in `recommender.py` sum to 1.0, so I tested genre at 0.10 and 0.40 against the current 0.20, which is the equivalent of the original question.

### What happened when I changed the weight on genre?

The #1 song stayed the same for all three profiles at every setting. The only change in which songs made the top 5 came in `pop_happy`:

| Profile | genre = 0.10 | genre = 0.20 (current) | genre = 0.40 |
|---|---|---|---|
| pop_happy #3–#5 | Calle Sol, Gym Hero, Bass Cathedral | Gym Hero, Calle Sol, Bass Cathedral | Gym Hero, Calle Sol, Bass Cathedral |
| pop_happy Gym Hero score | 0.72 | 0.75 | 0.79 |
| late_night_focus Coffee Shop Stories (jazz) | 0.79 | 0.76 | 0.71 |
| hip_hop_head #2–#4 | same order | same order | same order |

- **Lower genre weight (0.10):** The non-pop "energetic" and "euphoric" songs (Calle Sol, Bass Cathedral) climbed above Gym Hero, a pop song with the wrong mood. That is arguably a better fit for a "happy" listener.
- **Higher genre weight (0.40):** Gym Hero stayed ahead and the related-genre jazz song dropped from 0.79 to 0.71, because genre carried more of the score.
- **Hip hop:** This profile barely moved because the catalog has only four hip hop songs, so a heavier genre weight can't change much.

### What happened when I added or removed tempo and valence?

I removed tempo and valence from each profile to see how much they contribute. The top-5 order did not change for any profile, and scores dropped by 0.00 to 0.04 (for example, `pop_happy` Calle Sol 0.66 to 0.62). Without them, `HUMBLE.` and `No Role Modelz` tied at 0.71 for `hip_hop_head`. They carry only 0.12 of weight combined, and songs within a style cluster have similar tempo and valence, so they act mostly as small tiebreakers.

I also halved the energy weight (0.15 to 0.075). The ranking was identical for all three profiles and scores moved by 0.03 or less, because genre, mood and the other numeric traits already correlate with energy.

### How did the system behave for different types of users?

- **Realistic profiles** (`late_night_focus`, `hip_hop_head`, `pop_happy`): The exact genre and mood match ranked first (0.99 to 1.00), followed by related genres. The results matched my intuition.
- **Adversarial profiles** (12 edge cases, detailed below): These exposed silent failures (wrong-case or unknown labels and typo'd keys got no warning), ties (a genre-only profile put four hip hop songs at 1.00), inflated scores for profiles with few features, and no input validation (a non-numeric energy value crashed).

**Overall takeaway:** The rankings are stable under reasonable weight changes. The only place a weight change reshuffled the top 5 was `pop_happy` under a different genre weight. That robustness comes partly from the small 23-song catalog, so these experiments say more about the dataset than about the weights.


# Stress Testing with Diverse Profiles
## Edge Case Testing

I ran 12 adversarial profiles through `recommend_songs` (top 3 shown) to look for unexpected behavior.
"Full" below means the numeric targets from `LATE_NIGHT_FOCUS`.

| # | Profile | Top 3 results (score) | Finding |
|---|---------|-----------------------|---------|
| 1 | Full + `genre: "Lofi"` (capital L), mood focused | Focus Flow (0.79), Midnight Coding (0.68), Library Rain (0.67) | Genre match is case-sensitive, so the genre weight is silently lost. Numeric features hid the problem here. |
| 2 | Full + `genre: "k-pop"`, `mood: "bittersweet"` | Focus Flow (0.59), Midnight Coding (0.58), Library Rain (0.57) | Unknown labels get 0 credit with no warning. Results fall back to numeric features only. |
| 3 | `{"genre": "pop", "enrgy": 0.9}` (typo) | Sunrise City (1.00), Gym Hero (1.00), Rooftop Lights (0.50) | Typo'd key is ignored. Gym Hero (energy 0.93) and Sunrise City tie at a perfect 1.00. |
| 4 | `{}` | Sunrise City (0.00), Midnight Coding (0.00), Storm Runner (0.00) | All scores are 0, so the "ranking" is just CSV order. |
| 5 | `{"genre": "hip hop"}` | Concrete Kingdom (1.00), No Role Modelz (1.00), HUMBLE. (1.00) | Four-way tie, broken by CSV order. |

### Takeaways
- **Silent failures:** wrong-case labels (1), unknown labels (2), typo'd keys (3) and empty profiles (4) all run without errors but give degraded results.
- **Inflated scores:** with few features (3, 5, 10) weights are renormalized, so a match on one or two features reaches 1.00. Scores aren't comparable across profiles with different numbers of features.
- **Ties:** profiles with only categorical keys produce ties broken by CSV order (3, 5).
- **No validation:** out-of-range numbers (9) are accepted and a non-numeric value (12) crashes.
- **Possible fixes:** lowercase and strip categorical inputs, warn on unknown keys and labels, clamp numeric targets to their ranges, and add a secondary tiebreaker such as popularity.

1. wrong_case_genre (genre: "Lofi", mood focused, lofi-style numerics)

Focus Flow (lofi/focused) 0.79
Midnight Coding (lofi/chill) 0.68
Library Rain (lofi/chill) 0.67
Coffee Shop Stories (jazz/relaxed) 0.66
Spacewalk Thoughts (ambient/chill) 0.62

2. unknown_genre_and_mood (k-pop / bittersweet, same numerics)

Focus Flow (lofi/focused) 0.59
Midnight Coding (lofi/chill) 0.58
Library Rain (lofi/chill) 0.57
Coffee Shop Stories (jazz/relaxed) 0.56
Spacewalk Thoughts (ambient/chill) 0.52

3. typo_key ({"genre": "pop", "enrgy": 0.9})

Sunrise City (pop/happy) 1.00
Gym Hero (pop/intense) 1.00
Rooftop Lights (indie pop/happy) 0.50
Midnight Coding (lofi/chill) 0.00
Storm Runner (rock/intense) 0.00

4. empty_profile ({})

Sunrise City (pop/happy) 0.00
Midnight Coding (lofi/chill) 0.00
Storm Runner (rock/intense) 0.00
Library Rain (lofi/chill) 0.00
Gym Hero (pop/intense) 0.00

5. genre_only ({"genre": "hip hop"})

Concrete Kingdom (hip hop/confident) 1.00
No Role Modelz (hip hop/reflective) 1.00
HUMBLE. (hip hop/defiant) 1.00
Ruff Ryders' Anthem (hip hop/aggressive) 1.00
Velvet Hours (r&b/romantic) 0.50


---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

**explained this in the model card in depth*

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this showed me that a recommender turns data into predictions by reducing everything to numbers and comparing them. Each song is a row of traits (genre, mood, energy, tempo and so on), the user is a profile of target values, and the "prediction" is a weighted score of how close each song sits to those targets. The weights are where the real decisions hide. Giving genre and mood 40% of the score, for example, quietly defines what the system thinks "your taste" means.(So essentially a decision matrix) My experiments showed how much the data matters too: changing the genre weight barely reordered the results, mostly because the 23-song catalog left few alternatives to rank. The system also never explains itself beyond the traits I chose to score, so it can look confident (a 1.00) when it has only checked one or two features.

Bias and unfairness start with who and what the data includes. My catalog has 23 songs across 17 genres, but 14 of those genres have a single song and hip hop, lofi and pop have most of the rest, so the system works best for listeners whose taste happens to be well represented. A country, folk or classical listener gets one good match and then filler, while a hip hop listener gets a full list. That is not because the model understands them less, but because the data does. Genres that are missing entirely (K-pop was one I tried) get no credit at all, so those listeners are effectively excluded, and nothing in the output tells them why. The same thing happens with people: my profiles assume a user can name one genre and one mood in exactly the spelling I used, which favors users who fit my assumptions and silently penalizes anyone who types a label I didn't anticipate or whose taste doesn't fit a single genre. This can go wrong in real-world products in a similar way: a small or skewed catalog looks like a working system, so the gaps go unnoticed, and the same patterns snowball once listening data is involved. Popular, well-represented genres get more exposure, which generates more data for them, while niche genres, regional music and the listeners who love them become harder to find and are dropped from what gets recommended. A recommender that never shows a group of users their own music can affect that music's audience, and because the exclusion happens without error messages or complaints, nobody is likely to notice it unless they test for it deliberately.
