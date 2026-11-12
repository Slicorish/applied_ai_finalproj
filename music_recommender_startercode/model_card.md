# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatcher 1.0**: a content-based, weighted-score music recommender.

---

## 2. Intended Use  

VibeMatcher takes a taste profile (a favorite genre, a favorite mood, and target values for things like energy, valence and tempo) and returns the 5 songs from a small catalog that best fit it, each with a score out of 1.00 and a short list of reasons.

It assumes the user can describe their taste up front as one fixed profile, that a person wants songs close to those targets, and that genre and mood labels are spelled exactly as they appear in the catalog. It does not learn from listening history, skips, or other users.


---

## 3. How the Model Works  

Every song in the catalog has 11 traits the model looks at: genre, mood, energy, valence (how happy it sounds), acousticness, danceability, tempo, speechiness (how much of it is spoken word), instrumentalness (how much has no vocals), popularity, and length.

A user's profile says what they want for each trait: a favorite genre and mood, plus an ideal number for the other attributes, like tempo.

For each song, the model asks how well it fits on each trait and gives a fit between 0 and 1:

- **Genre and mood:** an exact match scores 1. If the labels are in the same "family" (for example, chill, relaxed, peaceful and focused, or pop and indie pop), the song gets half credit. Otherwise it gets 0.
- **Everything else:** the fit is how close the song's number is to the user's ideal. A perfect hit is 1, and the further away it is, the lower the fit, down to 0.

Each trait then counts toward the final score by a different amount. Genre and mood matter most (20% each), energy is next (15%), and the rest share the remaining 45%. The song's final score is the weighted sum, so it lands between 0 and 1. If a profile leaves a trait out, that trait is skipped and the remaining weights are scaled up so they still add to 100%. The 5 highest-scoring songs are shown, along with the traits that matched well.

**Changes from the starter:**

- I implemented loading, scoring, ranking and explanations.
- I extended the catalog with four extra traits (speechiness, instrumentalness, popularity, length) so the profiles can describe more than genre and energy.
- I added "related" genre and mood families so near-misses earn partial credit instead of zero.
- Weights were renormalized for partial profiles.
- Explanations were only built for the top 5, to keep scoring fast.
- A command-line runner prints each recommendation as a card with a score bar and reasons.

---

## 4. Data  

The catalog is `data/songs.csv`, with **23 songs** and 14 columns per song: id, title, artist, genre, mood, and nine numeric traits.

**Genres (17):** pop, indie pop, lofi, ambient, jazz, synthwave, rock, metal, hip hop, r&b, country, reggaeton, classical, folk, edm, blues and world. Hip hop has 4 songs, lofi has 3, pop has 2, and each of the other 14 genres has exactly one.

**Moods (19):** happy, chill, intense, relaxed, moody, focused, nostalgic, confident, romantic, angry, energetic, melancholic, peaceful, euphoric, sad, uplifting, reflective, defiant, aggressive.

**What I changed:** the starter file had 10 songs and 5 numeric traits (energy, tempo, valence, danceability, acousticness). I grew it to 23 songs and added speechiness, instrumentalness, popularity and duration. The catalog now includes four hip hop tracks with different moods (confident, reflective, defiant, aggressive), so hip hop profiles have something to choose between. (That's my favorite genre)

**What's missing:**

- Most genres have a single song, so there is little to choose from after the first match.
- There are no non-English-language, regional or fusion genres beyond one "world" track and one reggaeton track, and no sub-genres (for example, only one kind of rock or metal).
- The numeric traits are hand-written estimates, not measured from audio.
- There is no release year, language, lyrics theme, or listener data, so tastes based on era, language or lyrics can't be expressed.

---

## 5. Strengths  

**Users it serves well.** Anyone with a complete profile in a genre the catalog covers well. In testing, `late_night_focus` (lofi/focused), `hip_hop_head` and `pop_happy` all put an exact genre-and-mood match first (scores 0.99 to 1.00), and the rest of the list made sense to me.

**Patterns it captures correctly.**

- The related-family feature behaves as expected. A lofi listener gets jazz and ambient next (Coffee Shop Stories, Spacewalk Thoughts), a pop listener gets indie pop (Rooftop Lights), and a hip hop listener gets r&b.
- Numeric traits separate genres that share a label. Within hip hop, the high-energy, high-speechiness "Ruff Ryders' Anthem" outranks the calmer "No Role Modelz" for the high-energy hip_hop_head profile.
- When two songs share a genre, mood and numbers decide the order, so a "chill" lofi song ranks below the "focused" one for a focus profile.
- Each recommendation comes with reasons ("mood match (focused) +0.20; energy close to target +0.15"), so you can see why a song ranked where it did.

---

## 6. Limitations and Bias 

1. Exact-match genre and mood dominate (0.40 of the score). A genre or mood match is worth 1.0 and anything else is worth 0 or 0.5, so staying in the user's stated genre is always the safest way to rank high. There is no diversity or novelty term, so the top 5 can't show anything outside the user's declared taste.
2. The catalog is thin and skewed. songs.csv has 23 songs across 17 genres. Hip hop has 4, lofi 3 and pop 2, and the other 14 genres have exactly one song each. After a user's single match in one of those genres, the rest of the list is filler.
3. Related-group credit is hand-coded and uneven. RELATED_GENRES leaves 6 genres with no relatives: country, reggaeton, classical, folk, blues and world. RELATED_MOODS leaves out moody, romantic and confident. Users of those genres and moods get all-or-nothing credit, while lofi, jazz and ambient users get a soft landing in each other's music. That reinforces a lofi-style bubble.
4. Genre-correlated features are counted twice. Speechiness (0.08), instrumentalness (0.07) and acousticness (0.07) mostly encode genre. Mood is also correlated with energy and valence. The effective weight on "stay in your genre" is therefore well above the nominal 0.20.
5. Scoring rewards closeness to the target, never direction. Every numeric feature scores 1 - distance, so nothing ever pulls a user toward a nearby but different sound.
6. Arbitrary numeric ranges. A 300-second range for duration_sec penalizes long tracks such as classical (358s) and ambient (312s) whenever a user has a duration target. A high popularity target favors mainstream songs, though only at 0.04 weight.
7. Ties are broken by CSV order. Songs listed earlier get more exposure, and nothing caps repeat artists (Neon Echo and LoRoom each appear twice).

*Summary of the highest-impact weakness*
The biggest weakness is the 40% exact-match weight on genre and mood, combined with a catalog where 14 of 17 genres have one song or fewer than a handful. In my earlier test, a {"genre": "hip hop"} profile put four hip hop songs tied at 1.00 in the top 4. The fifth was an r&b song at 0.50, from the hand-coded related group. Users never see anything outside their declared genre unless it happens to sit in a hand-picked related group. With no diversity re-ranking or exploration term, that makes a self-reinforcing filter bubble, and for the 12 single-song genres the results after #1 are arbitrary. The fix I'd try first is to lower the genre and mood weight, or add a diversity re-rank (for example, cap each genre at 2 of the top 5). 

---

## 7. Evaluation  

**Profiles tested.** I ran three realistic profiles from `main.py` (`late_night_focus`, `hip_hop_head`, `pop_happy`) and 12 adversarial edge-case profiles meant to break the scoring: wrong-case genre (`"Lofi"`), unknown genre/mood (`"k-pop"`), a typo'd key (`"enrgy"`), an empty profile, a genre-only profile, contradictory tastes (lofi + angry + high energy), an impossible combination (loud and acoustic), a genre/mood pair that no song satisfies (pop + sad), out-of-range numbers, an ungrouped genre (country), a related-group case (jazz), and a non-numeric value (`"energy": "high"`).

**What I looked for.** For the realistic profiles, I checked whether the top 5 matched my intuition and whether the "Why" reasons made sense. For the edge cases, I looked for silent failures (bad results with no error), scores that looked too confident, ties, and crashes.

**Realistic profiles (top 5, score).**

| Profile | Top 5 |
|---|---|
| late_night_focus | Focus Flow (0.99), Midnight Coding (0.88), Library Rain (0.87), Coffee Shop Stories (0.76), Spacewalk Thoughts (0.72) |
| hip_hop_head | Concrete Kingdom (1.00), Ruff Ryders' Anthem (0.77), No Role Modelz (0.74), HUMBLE. (0.71), Velvet Hours (0.60) |
| pop_happy | Sunrise City (0.99), Rooftop Lights (0.87), Gym Hero (0.75), Calle Sol (0.66), Bass Cathedral (0.63) |

All three matched my expectations. The top song was an exact genre and mood match, and the list then moved outward through related genres (jazz and ambient for lofi, r&b for hip hop, indie pop for pop). The 1.00 and 0.99 top scores show that the profiles are fully satisfied only by one song each.

**Edge cases: what surprised me.**

- **Silent failures.** `"Lofi"` (capital L) and `"k-pop"` ran without errors but the genre weight was lost, and the lists were identical except for scores about 0.20 lower. The typo `"enrgy"` was ignored, so Gym Hero tied Sunrise City at a perfect 1.00 for a pop profile that asked for energy 0.9. An empty profile scored every song 0.00 and returned the songs in CSV order.
- **Ties and inflated scores.** A `{"genre": "hip hop"}` profile put four hip hop songs tied at 1.00. A country/nostalgic profile scored 1.00 for Dust Road Home because only three features were active and all matched. Because weights are renormalized over the keys present, scores aren't comparable across profiles with different numbers of features.
- **Genre is weaker than expected in conflicts.** For lofi + angry + energy 0.97, the top result was Iron Requiem (metal/angry, 0.70) and no lofi song appeared, so mood and numeric features outweighed genre. The impossible loud-and-acoustic rock profile still gave Storm Runner 0.81, with no signal that the request was contradictory.
- **Genre can outrank emotional fit.** For pop + sad, the best result was a blues song (0.59), but a happy pop song (Sunrise City, 0.47) ranked #2 on genre alone.
- **No validation.** Out-of-range values (energy 1.5, popularity 250) were accepted and simply zeroed those features' scores, and `"energy": "high"` crashed with a `TypeError`.

**Simple comparisons.** I compared the `jazz + relaxed` profile (an exact match exists, so Coffee Shop Stories scored 1.00 and lofi songs followed at 0.67 via related-group credit) against the ungrouped `country + nostalgic` profile (an exact match scored 1.00, but #2 and #3 were sad and reflective songs from unrelated genres at 0.43 and 0.41). This showed how much the hand-coded related groups shape what appears after the first result.

I did not compute numeric metrics; evaluation was manual inspection of the ranked lists and the explanations.

---

## 8. Future Work  

**Input edge-case handling.** Lowercase and trim genre and mood inputs, warn on unknown keys (for example, `enrgy`) and unknown genres or moods, clamp numeric targets to their valid ranges, and reject non-numeric values with a clear message instead of crashing. The empty profile should return an error instead of 5 songs scored 0.00.

**Diversity.** Re-rank the top results so no more than 2 of 5 share a genre, and cap repeat artists. Lowering the combined 40% genre and mood weight would also let adjacent styles surface more often. Break ties with a secondary signal (such as popularity) instead of CSV order.

**A bigger and better catalog.** Adding several songs per genre, more sub-genres and languages, and measured audio features instead of hand-written ones will increase accuracy. Consequently, a larger catalog will also require the `heapq.nlargest` version noted in the code comments to pay off in future versions.

**Better related-genre logic.** Replace the hand-made groups with similarity learned from the data (for example, distance between songs' numeric traits), and add the missing families for country, folk, blues, classical, world and reggaeton.

**Better explanations.** Report *why not* as well as why: say which traits missed ("energy far from target") and flag when a score is inflated because only a few features were supplied. Show scores on a comparable scale across profiles with different numbers of features.

**More complex tastes.** Let a user list several favorite genres or moods, give each trait its own importance, or describe contexts (studying versus working out) that switch profiles. Long term, learn from skips and replays instead of a one-time profile.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  

**What I learned.** I learned how complex the logic for recommender systems actually are. I don't think that it's something that I actually took into account. Especially the layer where the system from other users' behavior and preferences. I also learned more about the mathematical operations and algorithms that go into analyzing and computing recommendations. 

- Something unexpected or interesting you discovered 
**Interesting discoveries**  I took an AI cohort class and we covered the topic of decision matrices when trying to produce efficient/accurate decisions with logic, and I found it interesting and cool that the same decision matrices concept essentially can be applied here in this lab as well. 

- How this changed the way you think about music recommendation apps  
**What changed my thinking** I definitely have a more thorough understanding of how music recommendation works and I have a lot more appreciation for the developers who came up with the systems and algorithms lol. I've also realized that recommendations can be rather simple or complex, it essentially just mathematical algorithms when you boil it down.x
