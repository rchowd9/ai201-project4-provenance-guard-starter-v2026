#!/usr/bin/env python3
"""
Measure what one run of Provenance Guard actually costs.

    python serve.py              # in one terminal (model warm, debug off)
    python measure_cost.py       # in another: 10 runs, then the averages

**What "cost" means here.** Nothing calls a paid API, so there is no spend and
no billed tokens. The real cost of a run is the compute the local gpt2 pass
uses: CPU-seconds and wall-clock seconds on this machine. The secondary unit is
gpt2 tokens read per run, because that's what the CPU time scales with.

**How it's measured** (all by the running service, not estimated):

  * cpu_ms       `time.process_time()` delta across the request, taken in
                 instrumentation.py's before/after hooks. It is CPU time for the
                 whole server process, summed across cores — torch spreads one
                 gpt2 pass over several threads, so this can exceed wall time.
                 Because it is process-wide, runs are sent strictly one at a
                 time, so no other request's CPU is counted in.
  * duration_ms  server wall time, `time.perf_counter()` across the request.
  * signal_one   wall time of the gpt2 stage alone.
  * client_ms    wall time seen by this script, including HTTP + JSON.
  * model_tokens tokens gpt2 read (capped at DETECTOR_MAX_TOKENS = 400).

Each request carries its own X-Request-ID, and the numbers are read back from
that request's record in logs/requests.jsonl, so every figure in the report is
one the service wrote down at the time.

A baseline of 10 `GET /health` calls is measured the same way, to show the
CPU floor of a request that runs no model.

Writes results/cost_<date>.md.
"""

import argparse
import datetime as dt
import json
import os
import platform
import statistics
import sys
import time
import uuid

import config
import instrumentation

# A fixed, ordinary-length submission (~230 words, a short essay), so every run
# does the same work and runs on different days compare.
RUN_TEXT = (
    "Last spring our neighbourhood started a shared garden on the empty lot behind "
    "the library. Nobody really knew what they were doing at first. We argued for a "
    "whole evening about whether to build raised beds or dig straight into the "
    "ground, and in the end we did half of each because nobody would back down. "
    "The raised beds won, obviously. The soil in the lot was mostly gravel and old "
    "brick, and the carrots we planted there came up stunted and forked, like "
    "little orange hands. Mrs. Okafor, who is eighty-one and has gardened her whole "
    "life, laughed at them for a week. She brought cuttings from her own tomatoes "
    "and showed the kids how to pinch out the side shoots. By July we had more "
    "courgettes than anyone could eat, and people started leaving them on doorsteps "
    "at night like a prank. The library let us put a table out front with a sign "
    "saying take what you need. Some weeks it emptied in an hour. I think the "
    "garden mattered less for the food than for the excuse it gave people to talk. "
    "I learned the names of a dozen neighbours I had walked past for years. When "
    "the first frost came in October we pulled up the last of the beans together "
    "and somebody brought soup. We are already planning next year, and this time "
    "we are starting with compost."
)


def _send(session, base, method, path, body=None):
    rid = f"cost-{uuid.uuid4().hex[:8]}"
    start = time.perf_counter()
    r = session.request(method, f"{base}{path}", json=body,
                        headers={"X-Request-ID": rid}, timeout=180)
    return rid, r, (time.perf_counter() - start) * 1000


def _records_by_id(ids):
    wanted = set(ids)
    found = {r["request_id"]: r for r in instrumentation.read_requests()
             if r.get("request_id") in wanted}
    return [found.get(i) for i in ids]


def _summary(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return {"mean": None, "sd": None, "min": None, "max": None}
    return {
        "mean": statistics.mean(vals),
        "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        "min": min(vals),
        "max": max(vals),
    }


def _fmt(x, nd=1):
    return "—" if x is None else f"{x:,.{nd}f}"


def main():
    ap = argparse.ArgumentParser(description="Measure the compute cost of one run.")
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--base", default=f"http://127.0.0.1:{config.PORT}")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    import requests

    session = requests.Session()
    try:
        health = session.get(f"{args.base}/health", timeout=5).json()
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"Service isn't answering at {args.base} ({exc}). Start it: python serve.py")
    if not health.get("detector_loaded"):
        print("Note: model not loaded yet, so run 1 will include the model load. "
              "Start with `python serve.py` to keep load cost out of the runs.")

    # Baseline: a request that runs no model.
    base_ids = [_send(session, args.base, "GET", "/health")[0] for _ in range(args.runs)]

    print(f"Sending {args.runs} runs, one at a time ({len(RUN_TEXT.split())} words each)…")
    run_ids, client_ms, statuses = [], [], []
    for i in range(args.runs):
        rid, r, ms = _send(session, args.base, "POST", "/submit",
                           {"text": RUN_TEXT, "creator_id": f"cost_run_{i + 1:02d}"})
        run_ids.append(rid)
        client_ms.append(ms)
        statuses.append(r.status_code)
        print(f"  run {i + 1:>2}: {r.status_code}  {ms:7.1f} ms")
    if any(s != 200 for s in statuses):
        print(f"Warning: not every run returned 200 ({statuses}). Rate limited? "
              "Those runs are excluded from the averages.")

    time.sleep(0.2)  # teardown writes the record just after the response
    recs = _records_by_id(run_ids)
    base_recs = _records_by_id(base_ids)
    if any(r is None for r in recs):
        sys.exit("Some run records are missing from logs/requests.jsonl — is this "
                 "script reading the same repo the service is running from?")

    rows = []
    for i, (rec, cms) in enumerate(zip(recs, client_ms), 1):
        ok = rec["status"] == 200
        cpu, wall = rec.get("cpu_ms"), rec.get("duration_ms")
        tokens = rec.get("model_tokens")
        rows.append({
            "run": i, "ok": ok, "request_id": rec["request_id"],
            "client_ms": cms, "wall_ms": wall, "cpu_ms": cpu,
            "signal_one_ms": rec.get("stages_ms", {}).get("signal_one"),
            "cores": (cpu / wall) if cpu and wall else None,
            "tokens": tokens,
            "cpu_ms_per_token": (cpu / tokens) if cpu and tokens else None,
            "rss_mb": rec.get("rss_mb"),
            "guess": rec.get("output", {}).get("guess"),
        })
    good = [r for r in rows if r["ok"]]

    s = {k: _summary([r[k] for r in good])
         for k in ("client_ms", "wall_ms", "cpu_ms", "signal_one_ms", "cores",
                   "tokens", "cpu_ms_per_token", "rss_mb")}
    b_cpu = _summary([r.get("cpu_ms") for r in base_recs if r])
    b_wall = _summary([r.get("duration_ms") for r in base_recs if r])

    try:
        import torch
        torch_threads = torch.get_num_threads()
    except Exception:  # noqa: BLE001
        torch_threads = None

    cpu_s = s["cpu_ms"]["mean"] / 1000
    wall_s = s["wall_ms"]["mean"] / 1000
    now = dt.datetime.now()
    L = [f"# Cost of one run — {now:%Y-%m-%d %H:%M}", ""]
    L += [
        "**The cost unit is compute, not money.** Provenance Guard calls no paid "
        "API, so a run has no API spend and no billed tokens. What a run consumes "
        "is CPU time for one local gpt2 pass, so it's measured in CPU-seconds and "
        "wall-clock seconds, with gpt2 tokens read as the unit of work.",
        "",
        f"## Result — average of {len(good)} runs",
        "",
        "| Measure | Mean | SD | Min | Max |",
        "|---|---|---|---|---|",
        f"| **CPU time per run** (all cores) | **{_fmt(s['cpu_ms']['mean'])} ms** | {_fmt(s['cpu_ms']['sd'])} | {_fmt(s['cpu_ms']['min'])} | {_fmt(s['cpu_ms']['max'])} |",
        f"| **Wall time per run** (server) | **{_fmt(s['wall_ms']['mean'])} ms** | {_fmt(s['wall_ms']['sd'])} | {_fmt(s['wall_ms']['min'])} | {_fmt(s['wall_ms']['max'])} |",
        f"| of which signal one (gpt2) | {_fmt(s['signal_one_ms']['mean'])} ms | {_fmt(s['signal_one_ms']['sd'])} | {_fmt(s['signal_one_ms']['min'])} | {_fmt(s['signal_one_ms']['max'])} |",
        f"| Wall time seen by client | {_fmt(s['client_ms']['mean'])} ms | {_fmt(s['client_ms']['sd'])} | {_fmt(s['client_ms']['min'])} | {_fmt(s['client_ms']['max'])} |",
        f"| Cores busy (CPU ÷ wall) | {_fmt(s['cores']['mean'], 2)} | {_fmt(s['cores']['sd'], 2)} | {_fmt(s['cores']['min'], 2)} | {_fmt(s['cores']['max'], 2)} |",
        f"| gpt2 tokens read | {_fmt(s['tokens']['mean'], 0)} | {_fmt(s['tokens']['sd'], 0)} | {_fmt(s['tokens']['min'], 0)} | {_fmt(s['tokens']['max'], 0)} |",
        f"| CPU per token | {_fmt(s['cpu_ms_per_token']['mean'], 2)} ms | {_fmt(s['cpu_ms_per_token']['sd'], 2)} | {_fmt(s['cpu_ms_per_token']['min'], 2)} | {_fmt(s['cpu_ms_per_token']['max'], 2)} |",
        f"| Server memory (RSS) | {_fmt(s['rss_mb']['mean'], 0)} MB | | {_fmt(s['rss_mb']['min'], 0)} | {_fmt(s['rss_mb']['max'], 0)} |",
        "",
        f"Baseline, `GET /health` ×{len(base_recs)} (no model): CPU "
        f"{_fmt(b_cpu['mean'], 2)} ms, wall {_fmt(b_wall['mean'], 2)} ms. "
        "That is the cost of the framework alone; a run costs "
        f"{_fmt(s['cpu_ms']['mean'] / b_cpu['mean'], 0) if b_cpu['mean'] else '—'}× it.",
        "",
        "**What that comes to, from the measured mean (arithmetic, not a price list):**",
        "",
        f"- 1,000 runs ≈ **{cpu_s * 1000 / 60:,.1f} CPU-minutes**, "
        f"{wall_s * 1000 / 60:,.1f} minutes of wall time one at a time.",
        f"- One core-hour of CPU covers ≈ **{3600 / cpu_s:,.0f} runs**.",
        f"- One client sending back-to-back gets ≈ {1 / wall_s:,.1f} runs/s.",
        "",
        "## Every run",
        "",
        "| Run | Status | request_id | Client ms | Server wall ms | CPU ms | signal_one ms | Cores | Tokens | Guess |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r, st in zip(rows, statuses):
        L.append(f"| {r['run']} | {st} | `{r['request_id']}` | {_fmt(r['client_ms'])} | "
                 f"{_fmt(r['wall_ms'])} | {_fmt(r['cpu_ms'])} | {_fmt(r['signal_one_ms'])} | "
                 f"{_fmt(r['cores'], 2)} | {r['tokens']} | {r['guess']} |")
    L += [
        "",
        "## How this was measured",
        "",
        "- **The run:** one `POST /submit` with the same fixed ~230-word text "
        f"({len(RUN_TEXT)} chars), sent {args.runs} times, strictly one after "
        "another, each under its own creator_id so the rate limit can't interfere.",
        "- **CPU time:** the service records `time.process_time()` at the start "
        "and end of every request (`instrumentation.py`, before/after hooks) and "
        "logs the difference as `cpu_ms`. That's CPU time for the whole server "
        "process, summed over every core torch used, so it can exceed wall time. "
        "Because it's process-wide, the runs never overlap.",
        "- **Wall time:** `time.perf_counter()` across the same request, logged as "
        "`duration_ms`. Signal one's share is the `signal_one` stage timer.",
        "- **Tokens:** the gpt2 tokenizer's count for the text, capped at "
        f"{config.DETECTOR_MAX_TOKENS}, logged as `model_tokens`.",
        "- **Source:** every number above was read back from that request's "
        "record in `logs/requests.jsonl` by its `X-Request-ID`, not computed by "
        "this script. Client time is the only figure taken here.",
        "- **Model state:** the service was started with `serve.py`, so gpt2 was "
        "already in memory and no run includes the model load "
        + (f"(`detector_loaded` was {health.get('detector_loaded')} before run 1)." ),
        "",
        "**Machine:** "
        f"{platform.system()} {platform.release()}, {platform.processor() or platform.machine()}, "
        f"{os.cpu_count()} logical CPUs, torch default {torch_threads} threads, "
        f"Python {platform.python_version()}, model `{config.DETECTOR_MODEL}`, CPU only. "
        "These numbers belong to this machine; a different CPU gives different ones, "
        "which is why it's measured and not looked up.",
        "",
    ]
    report = "\n".join(L)
    print()
    print(report)
    if not args.no_write:
        config.RESULTS_DIR.mkdir(exist_ok=True)
        out = config.RESULTS_DIR / f"cost_{now:%Y-%m-%d_%H%M}.md"
        out.write_text(report, encoding="utf-8")
        print(f"Wrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
