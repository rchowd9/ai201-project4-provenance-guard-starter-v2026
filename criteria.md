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

---

# Extension criteria — Shape A, deploy and instrument

Five criteria for the extension: `serve.py`, the structured run log
(`logs/requests.jsonl`), `/metrics`, and the cost measurement. All five are
about the new part. Each one names how it gets checked, and the targets come
from numbers I've already measured on this machine, so I can tell whether each
one is reachable and still a stretch.

---

## 1. Every request leaves exactly one record

In a mixed batch of 60 requests sent with my own `X-Request-ID` values (30
valid submissions, the 12 malformed-request rows from the attack set, 15
submissions from one creator so at least 3 get a `429`, and 3 appeals,
including one with an unknown `content_id`), **60 of 60 request ids appear in
`logs/requests.jsonl` exactly once**: 0 missing and 0 duplicated. Every record
has a non-empty `timestamp`, `outcome`, `duration_ms`, `input` and `output`,
and its `status` matches the status code the client received.

**Why this target:** In Path B the log is the only evidence. There is no host
dashboard to fall back on. A request with no record is invisible, and the
README already names the worst version of that: a flood of `429`s that leaves
no trace looks like a quiet afternoon. So the target is 100%, not 99%, because
the one missing record is the one I'd never know to look for. Duplicates count
as failures too, because `perf_report.py` and `measure_cost.py` average over
the records. A doubled record skews every number and makes one request look
like two.

> **Result (unit 9, 3 trials, `run_extension_eval.py`): MET.**
> Trial 1: 60/60 logged once, 0 missing, 0 duplicated, 0 status mismatches,
> 0 incomplete records, 3 × 429. Trials 2 and 3: identical. All three trials
> also had status codes 46 × 200, 10 × 400, 1 × 404, 3 × 429, and every 429
> left a record.

---

## 2. When something breaks, the caller gets an answer and the log gets the cause

Three forced failures:

- a stage that raises mid-request (an exception injected into signal two),
  under both `serve.py` and `python app.py` debug mode;
- `/submit` while the model can't load (`AI201_DETECTOR_MODEL` set to a model
  that doesn't exist);
- `serve.py` started with that same bad model.

**Each of the 4 cases must leave a record with `outcome: "error"`, the
`exception` type and message, and (for the mid-request crash) the
`failed_stage`.** The `/submit` case must return a JSON `503` within **30
seconds**, not a hang or an HTML error page. The bad start must exit without
opening the port and leave one `event: "startup"` error record.

**Why this target:** This is the bad path. The interesting failure isn't the
crash itself but a crash that leaves no record. Before I fixed it, a crash
under `python app.py` did exactly that, because debug mode lets the exception
escape before the after-request hook runs. Every case has to leave a record,
because each one fails a different way. I chose 30 s for the `503` because a
successful model load takes 10–13 s here. Failing should never take longer
than succeeding plus a margin. A writer who waits longer than that with no
answer will resubmit, and every retry repeats the same failure. A stricter
limit like 5 s could fail just because the Hugging Face lookup is slow, which
says nothing about my code. A looser one like 120 s, gunicorn's timeout,
would count a two-minute wait as a pass.

> **Result (unit 9, 3 trials): MET.** 4/4 cases in every trial.
> - **Crashes (a) and (b):** one `outcome: "error"` record each, with
>   `InjectedFault`, its message, and `failed_stage: "signal_two"`.
> - **Model can't load (c):** a JSON 503 in 6.34 s, 7.57 s and 6.84 s, all
>   under 30 s, with `DetectorUnavailable` in the record.
> - **Bad start (d):** exit code 1 in every trial, the port never opened, and
>   exactly one `startup` error record.
>
> One difference from the wording: debug mode ran as
> `flask --app app run --debug --no-reload`, not `python app.py`. It's the
> same app and the same debug-mode exception handling, without the reloader's
> second process, which the harness couldn't reliably shut down.

---

## 3. One run costs at most 5.0 CPU-seconds and 1.5 wall-seconds

Across **3 trials** of `python measure_cost.py` (10 sequential runs of the
fixed 234-word text each, against `serve.py`), the mean CPU time per run is
**≤ 5.0 CPU-seconds** and the mean server wall time is **≤ 1.5 s** in every
trial.

**Why this target:** The measured mean is 4.16 CPU-s (SD 0.21) and 1.17 s
wall (SD 0.19). The targets leave about 20–30% headroom for the noise I've
seen between runs (single runs reached 4.56 CPU-s and 1.50 s), but no more.
A 4.0 CPU-s limit would fail on this machine's normal variation. A 10 CPU-s
limit would pass even if every run doubled in cost, for example if someone
raised `DETECTOR_MAX_TOKENS` from 400 to 1,024 or loaded a larger model, and
that's the regression this should catch. Compute is the real cost of this
system: about 866 runs per core-hour. A run that quietly costs 20% more is
20% fewer writers served on the same machine.

> **Result (unit 9, 3 trials): MET.** Mean CPU per run 3.81, 3.60 and
> 3.52 CPU-s (all ≤ 5.0). Mean wall time 0.91, 0.95 and 0.99 s (all ≤ 1.5),
> with p95 at 0.97, 1.15 and 1.35 s. The 10 runs used the same fixed text and
> the same `cpu_ms`/`duration_ms` records as `measure_cost.py`, but were sent
> by `run_extension_eval.py::phase_a` so they'd be the first requests after a
> fresh start, which criterion 4 also needs.

---

## 4. The first request after startup costs no more than the rest

In each of the **3 trials** above, run 1's wall time is **≤ 1.5× the median
of runs 2–10**, measured on a freshly started `serve.py` (restarted before
each trial).

**Why this target:** This is the failure the cost measurement caught. Before
the warm-up fix, run 1 took 6.06 s against a median of about 1.06 s, 5.7×,
because torch's one-time setup landed in the first writer's request even
though the model was "loaded". After the fix it was 1.08 s. I chose 1.5×
because ordinary run-to-run spread reaches about 1.4× the median (the slowest
normal run was 1.50 s against about 1.08 s), so 1.5× allows for that noise
without letting the bug back in. A 2× limit would catch the original 5.7×
problem but miss a partial regression, such as a 2-second first request, and
that's still a writer waiting for setup that should have happened at startup.

> **Result (unit 9, 3 trials): MET.** Run 1 against the median of runs 2–10:
> 0.84 s vs 0.93 s (0.91×), 0.94 s vs 0.94 s (1.00×), and 0.86 s vs 0.89 s
> (0.96×). All are ≤ 1.5×, on a freshly started `serve.py` each trial.

---

## 5. Memory stays within the documented requirement and doesn't creep

Over **100 sequential submissions** to one `serve.py` process
(`perf_report.py --probe 100`), **peak RSS stays ≤ 1,536 MB (1.5 GB)**, and
the mean RSS of the last 10 requests is **no more than 100 MB above** the mean
of requests 11–20.

**Why this target:** RUNNING.md tells anyone running this to have "at least
1.5 GB free". If the service goes above that, the documented requirement is
wrong, and on a smaller machine it gets killed partway through. The highest
I've measured is 1,480 MB after a flood, so 1.5 GB is a real limit with only
about 4% spare. The second number checks for memory creep (growth that never
comes back down). Idle RSS jumped from 383 MB to 881 MB once warm-up ran a
real pass, and rose further under traffic. Growth that levels off is fine;
growth that keeps climbing across 100 requests is a leak, and a leak turns
into an out-of-memory crash on a long-running local service. I start the
comparison at requests 11–20 rather than 1–10 so the expected early growth
from torch's buffers doesn't count as a leak. A 50 MB limit would flag normal
allocator noise, and a 500 MB limit would let a leak run for hours before it
showed.

> **Result (unit 9, 3 trials): MISSED, both parts, in all 3 trials.**
>
> | Trial | Peak RSS (target ≤ 1,536 MB) | Creep, last 10 vs requests 11–20 (target ≤ +100 MB) |
> |---|---|---|
> | 1 | 3,019 MB | +1,512 MB (1,415 → 2,926) |
> | 2 | 3,037 MB | +1,526 MB (1,419 → 2,945) |
> | 3 | 3,028 MB | +1,520 MB (1,420 → 2,939) |
>
> RSS rose on 97–98 of 99 steps, and every trial crossed 1,536 MB at request
> 22 of the 100. The 100 submissions used `perf_report.py`'s probe texts,
> sent by `run_extension_eval.py::phase_a` to the same process right after the
> 10 runs for criteria 3 and 4.
>
> **Where:** the serving stage (`serve.py`'s Windows fallback, Flask's threaded
> server) together with signal one (`detector.model_signal`, torch).
>
> **How:** Flask's threaded server starts a new thread for every request.
> The first time a thread runs the gpt2 pass, torch sets up about 19 MB of
> state for that thread, and doesn't release it when the thread ends. Each
> submission leaves about 19 MB behind, so memory grows in a straight line
> and never levels off.
>
> **How I know:**
> - Without the server, 60 calls each of stylometry, `model_signal`, and the
>   full `/submit` through Flask's test client added only 0–0.8 MB per call.
> - Calling `model_signal` on a new thread each time added **+19.0 MB per
>   call**.
> - A reused pool of 4 threads added +2.5 MB per call, which is the pool
>   threads' one-time cost.
> - New threads that never run torch added nothing.
>
> The target stays at 1,536 MB. The fix is to run gpt2 on threads that are
> reused, not one per request.
