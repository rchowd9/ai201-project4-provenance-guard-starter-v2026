"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies. ← TODO

    Returns:
        A float. Decide yourself what scale it's on and which direction means
        "more human" — then write that down, because your combining rule
        depends on knowing it.

    A hint on what you're reaching for: the standard deviation of sentence
    lengths, probably divided by the mean so a long text and a short one are
    comparable. `statistics.stdev` is imported for you.

    Watch the edge case: a one-sentence submission has no spread at all, and
    `stdev` raises on fewer than two values. Decide what that should return
    before the attack set decides for you.

    My choice: the coefficient of variation (stdev / mean) of sentence lengths
    in words. 0.0 means every sentence is the same length; human prose usually
    sits around 0.5–0.8, generated prose nearer 0.2–0.4. **Higher = more
    human.** Fewer than two sentences returns 0.0, and `style_signal` treats
    that as "no evidence" rather than "perfectly even" so a one-sentence
    submission isn't pushed toward AI.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    return round(statistics.stdev(lengths) / mean, 4)


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words. ← TODO

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    Worth knowing before you rely on it: this measure falls as text gets
    longer, because common words repeat. Two texts of different lengths aren't
    directly comparable on it, and if your test inputs vary a lot in length,
    that alone can look like a signal.

    My choice: a moving-average type-token ratio. Slide a 50-word window along
    the text, take unique/total inside each window, and average. Every window
    is the same size, so a 300-word essay and a 60-word paragraph are measured
    on the same footing. Text shorter than the window falls back to the plain
    ratio. **Higher = more human.**
    """
    toks = words(text)
    if not toks:
        return 0.0
    window = 50
    if len(toks) <= window:
        return round(len(set(toks)) / len(toks), 4)
    ratios = [
        len(set(toks[i:i + window])) / window
        for i in range(len(toks) - window + 1)
    ]
    return round(statistics.mean(ratios), 4)


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to length. ← TODO

    Returns:
        A float. Whether you count all punctuation or only some kinds — commas,
        semicolons, dashes — is a real choice. Semicolons and em dashes are
        more interesting than full stops, because they vary more between
        writers.

    My choice: weighted punctuation marks per word. Full stops and commas
    count half (everyone uses them); everything else — ; : ! ? ( ) " dashes,
    ellipses — counts one. Plain comma-and-full-stop prose lands around
    0.05–0.08; prose with personal tics goes well above 0.1. **Higher = more
    human.**

    Worth knowing: recent chat models are fond of em dashes, so this measure
    can read their output as *more* human. It is the weakest of the three and
    weighted that way in `style_signal`.
    """
    n_words = len(words(text))
    if n_words == 0:
        return 0.0
    common = len(re.findall(r"[.,]", text))
    other = len(re.findall(r"[;:!?()\"“”—–…]|--|(?<=\s)-(?=\s)", text))
    return round((0.5 * common + other) / n_words, 4)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.** ← TODO

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Which direction each measure points. Low spread means more AI-ish, so
         it needs flipping. Work out which of your three need that.
      2. How to get each onto a comparable scale. A raw type-token ratio sits
         between 0 and 1; a raw punctuation count doesn't. Adding them
         unscaled means whichever has the bigger numbers wins by default.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.

    My decisions:

      1. All three measures point the same way (higher = more human), so all
         three get flipped.
      2. Each is mapped linearly onto 0–1 between a "clearly AI" and a "clearly
         human" anchor, then clamped, so each contributes on the same scale:

             spread       0.20 -> 1.0 (AI)   0.70 -> 0.0 (human)
             vocabulary   0.68 -> 1.0        0.82 -> 0.0
             punctuation  0.04 -> 1.0        0.14 -> 0.0

      3. Weights 0.45 spread, 0.35 vocabulary, 0.20 punctuation. Spread is
         the measure the AI/human difference shows up in most reliably;
         punctuation is the noisiest (see its docstring).
      4. Short text is pulled toward 0.5. Below about 150 words these measures
         are mostly noise, and noise should read as "unsure", not as a verdict.
         Fewer than two sentences drops the spread measure entirely.
    """
    def flip(value, ai_anchor, human_anchor):
        x = (human_anchor - value) / (human_anchor - ai_anchor)
        return min(max(x, 0.0), 1.0)

    n_words = len(words(text))
    if n_words == 0:
        return 0.5

    parts = [
        (0.35, flip(type_token_ratio(text), 0.68, 0.82)),
        (0.20, flip(punctuation_density(text), 0.04, 0.14)),
    ]
    if len(sentences(text)) >= 2:
        parts.append((0.45, flip(sentence_length_spread(text), 0.20, 0.70)))

    raw = sum(w * v for w, v in parts) / sum(w for w, _ in parts)

    confidence = min(n_words / 150, 1.0)
    score = 0.5 + (raw - 0.5) * confidence
    return round(score, 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
