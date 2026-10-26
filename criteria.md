# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False Positives

Of 10 pieces of completely human-written text I submit, at most 1 is labeled with a high-confidence AI classification across all three evaluation trials.

**Why this target:** 
False accusations carry a much higher social and professional penalty for a writer than a missed detection[cite: 3]. Setting the threshold at a maximum of 1 out of 10 ensures the detector remains trustworthy and protects human-authored content from false positives[cite: 3].

---

## 2. Score Spread

When testing clearly-AI generated text versus clearly-human text, the average confidence score difference between the two groups must be at least 0.50 points on a 0.0 to 1.0 scale.

**Why this target:** 
A viable detection system needs a distinct separation between machine-generated and human-authored characteristics rather than clustering everything in an ambiguous middle ground.

---

## 3. Label Coverage

All three defined system labels (e.g., human, uncertain/mixed, and high-confidence AI) are successfully returned at least once across a test set of 15 diverse text samples.

**Why this target:** 
If a label is mathematically or logically unreachable under normal operational bounds, it indicates a dead code path or broken threshold logic within the classification pipeline.

---

## 4. The Appeal Path

100% of submitted appeal requests on flagged assets successfully alter the asset status field (e.g., changing from flagged to under-review) and write a corresponding entry to the audit log.

**Why this target:** 
Users must have a reliable recourse when flagged incorrectly; an appeal path that fails to record or change status breaks accountability and transparency in content moderation.

---

## 5. Bad Input Handling

When `text` input is entirely missing, empty (`""`), or exceeds an enormous payload limit (>100,000 words), the endpoint gracefully returns a structured HTTP 400 Bad Request error rather than crashing or hanging indefinitely.

**Why this target:** 
Robust backend services must handle malformed, empty, or malicious edge-case payloads safely without causing unhandled internal server exceptions or service downtime.

---

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
