# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->



---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the text is to a language model.
`detector.py` runs gpt2 locally over the first 400 tokens and takes the
perplexity, which is how surprised the model is on average by each next token.
It maps that onto 0–1 with a logistic curve centred on perplexity 45. Low
perplexity gives a high score, and a high score means "more likely AI".

**Why that might differ between human and AI writing:** A language model writes
by picking a likely next word again and again, so its output sits in the
high-probability region that another language model also finds easy to predict.
Human writers make choices that aren't the statistically typical continuation:
a specific name instead of a general noun, an odd word, a sudden turn. Those
choices raise perplexity.

**What it can't see:** Who wrote the text. It sees only how *ordinary* the
wording is, and ordinary is not the same as machine-made. Specifically:

- **Plain human writing looks like AI.** Someone writing in a second language
  and sticking to words they're sure of, a younger writer, or anyone writing
  simply on purpose produces common words in short sentences. gpt2 finds that
  as predictable as generated text. These are the false accusations that hurt
  the most, and the people they hit have the least room to argue back.
- **Unusual-sounding AI looks human.** AI text generated at a high temperature,
  prompted to use rare or ornate vocabulary, run through a synonym-swapping
  paraphraser, or sprinkled with typos and slang becomes less predictable and
  scores as human. Dense, formal prose full of rare words scores human whoever
  wrote it.
- **Famous text looks like AI.** gpt2 saw well-known passages (song lyrics,
  scripture, the Declaration of Independence, widely copied boilerplate) during
  training, so it can predict them almost word for word. Human text that the
  model has memorised therefore gets very low perplexity.
- **It only reads the first 400 tokens.** Anything after the truncation point
  has no effect on the score, so a human-written opening followed by AI text,
  or the reverse, is judged entirely on the opening.
- **Short text isn't enough evidence.** A few sentences give a noisy average,
  and perplexity also moves with topic and length. A 2-sentence note and a
  400-token essay are being placed on the same curve.

### Signal two — the style signal

**What it measures:** The shape of the text as a sequence of characters, with no
model and no understanding of the words. It combines three measures:

- *Sentence-length spread:* the standard deviation of sentence lengths divided
  by the mean. Do sentences vary in length, or are they all about the same?
- *Type-token ratio:* unique words divided by total words, averaged over a
  sliding 50-word window so long and short texts are comparable. How much does
  the vocabulary repeat?
- *Punctuation density:* weighted punctuation marks per word. Full stops and
  commas count half, and semicolons, colons, dashes, brackets, quotation marks,
  ! and ? count one.

Each measure is flipped and mapped onto 0–1 between a "clearly AI" anchor and a
"clearly human" anchor. They are then weighted 0.55 spread, 0.25 vocabulary and
0.20 punctuation. Under 150 words, the score is pulled towards 0.5 in proportion
to the length, because a short text is mostly noise on these measures. Low
spread, low variety and plain punctuation push the score towards 1, which means
"more likely AI". This is the same direction as signal one.

**Why that might differ between human and AI writing:** Choosing the most likely
next word, averaged over a whole passage, tends to produce even, mid-length
sentences, a safe and repeated vocabulary, and regular comma-and-full-stop
punctuation. Human writing is lumpier. A three-word sentence sits next to a
forty-word one, words get repeated for emphasis or avoided out of habit, and
people have personal punctuation tics such as dashes, semicolons, ellipses or
none at all.

**What it can't see:** Meaning. It can't tell what the text says, so anything
that changes the shape without changing the substance moves the score, and those
changes are cheap to make on purpose:

- **Surface edits launder AI text.** Adding typos creates new "unique" words and
  raises the type-token ratio. Splitting some sentences and merging others
  raises the spread. Adding dashes, semicolons or a pasted quotation raises the
  punctuation score. None of these changes who wrote the text.
- **Asking the model for a different style.** "Vary your sentence lengths, use
  em dashes" is a one-line instruction to the generator, and it targets this
  signal's features directly.
- **Disciplined human writing looks like AI.** Plain, even, carefully edited
  prose with uniform sentences and conventional punctuation, such as a
  technical write-up, a non-native writer's careful English, or a student
  following a five-paragraph template, reads as machine-shaped. This
  is the same group of writers signal one already over-accuses, so when the two
  signals agree on them, the agreement isn't independent evidence.
- **The vocabulary measure rewards polish, not people.** The 50-word window
  removes the length effect, but in calibration a polished AI paragraph scored
  *more* varied (0.91) than a plainly written human one (0.74). What it really
  detects is plainness, which is why it carries only 0.25 of the weight.
- **Recent chat models like em dashes.** The punctuation measure counts dashes
  as a human habit, so it can read modern AI output as more human.
- **The text has to look like prose.** The splitter only breaks on `.`, `!` or
  `?` followed by a space, so a one-sentence submission, a list, a poem, text
  with no full stops, or text full of abbreviations ("Dr.", "e.g.") gives a
  meaningless spread. The word pattern `[a-z0-9']+` drops accented letters, so
  non-English or mixed-language text gets split into fragments.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** The two signals are averaged, but the more they disagree, the more
the decision goes to whichever signal says "more human". When they agree, the
result is a plain average. When they contradict each other, the lower score
counts for more, and at a gap of 0.5 or more it decides alone. Disagreement can
pull a score towards "human" but can never push it towards "AI". I would rather
let some AI text through than accuse a person on evidence that contradicts
itself. The cost is that an attacker only has to fool one of the two signals,
not both.

**The numbers** (in `config.py`):

- `WEIGHT_MODEL_SIGNAL = 0.5`, `WEIGHT_STYLE_SIGNAL = 0.5`: the starting weights
  when the signals agree.
- `DISAGREEMENT_PULL = 1.0`: for every point of gap between the two scores, that
  much weight moves from the higher signal to the lower one. The lower signal's
  weight is `0.5 + gap`, capped at 1.0.
- Example: model 0.9 and style 0.1 have a gap of 0.8, so the combined score is
  0.1. Model 0.6 and style 0.5 have a gap of 0.1, so the weights are 0.4 / 0.6
  and the combined score is 0.54.

Why not a plain 0.5 / 0.5 average: in calibration, the model signal hardly
separated anything. Every input scored between 0.62 and 0.87, and it rated
Thoreau as *more* AI-like than lightly-edited AI. A plain average would leave
the human label almost unreachable, because a text would need both signals low
at once.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**Calibration inputs** (both signals printed separately, as logged):

| Input | Words | model_score | style_score | Gap | combined_score |
|---|---|---|---|---|---|
| Clearly AI (generic "AI is transforming…" essay) | 136 | 0.8723 | 0.6395 | 0.23 | **0.7017** |
| Clearly human (Thoreau, *Walden*, 1854) | 172 | 0.6931 | 0.2815 | 0.41 | **0.3179** |
| Formal human (Darwin, *Origin of Species*, 1859) | 156 | 0.6869 | 0.4891 | 0.20 | **0.5489** |
| Lightly-edited AI (the AI essay with contractions, dashes, short sentences) | 122 | 0.6247 | 0.5239 | 0.10 | **0.5641** |
| Plain human (my own "grabbed some coffee" message) | 46 | 0.6255 | 0.6022 | 0.02 | **0.6133** |

What surprised me, and which signal caused it:

- **Formal human scores higher than lightly-edited AI on the model signal**
  (0.69 vs 0.62). Light edits such as contractions, a dash and a few short
  sentences were enough to make gpt2 less sure of the AI text. Older formal
  prose is predictable to gpt2, possibly because it saw these famous passages
  in training. The style signal ranked them correctly (0.49 vs 0.52), but by a
  tiny margin.
- **Lightly-edited AI lands in the middle (0.56), not near the clearly-AI
  input.** Neither signal holds up against light edits. That is the evasion
  route unit 8's attack set will use.
- **Plain human writing scores the most AI-like of everything except the
  clearly-AI input (0.61).** Both signals call it AI-ish, and because they
  agree, my rule gives them no reason to lean human. This is the
  writer Milestone 1 warned about. Both signals share the same blind spot, so
  their agreement isn't independent evidence.

**A case where my two signals split, and what my rule does with it:** Thoreau's
*Walden* opening. The model signal says 0.69, leaning AI, because gpt2 finds old,
famous prose predictable. The style signal says 0.28, clearly human, because the
sentence lengths swing from a nearly 60-word sentence to "I lived there two years and
two months." The gap is 0.41, so the style signal gets 0.91 of the weight and
the combined score is **0.32**. A plain average would have given 0.49, squarely
"unsure", for one of the most human texts I tested.



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Hey, just grabbed some coffee and was looking over the git logs we talked about earlier. Let me know if you want to sync up later this afternoon to review the remaining issues. We still need to finalize the backend configuration and check all the tests.", "creator_id": "riasat"}'
```

```json
{
  "confidence": 0.0,
  "content_id": "fbc43c99-e8b8-4371-9343-e01af8b6217e",
  "guess": "pending",
  "label": "pending",
  "model_score": 0.6255,
  "style_score": 0.6022
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=1"
```

```json
{
  "count": 1,
  "entries": [
    {
      "combined_score": null,
      "confidence": 0.0,
      "content_id": "fc469753-7fe8-4b12-aa57-458b67a111e6",
      "creator_id": "riasat",
      "guess": "pending",
      "label": "pending",
      "model_score": 0.6255,
      "status": "decided",
      "style_score": 0.0,
      "text": "Hey, just grabbed some coffee and was looking over the git logs we talked about earlier. Let me know if you want to sync up later this afternoon to review the remaining issues. We still need to finalize the backend configuration and check all the tests.",
      "timestamp": "2026-10-27T14:39:54+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
