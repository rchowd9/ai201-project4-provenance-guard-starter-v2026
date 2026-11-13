#!/usr/bin/env python3
"""
Latency breakdown and load observation for Provenance Guard.

    python serve.py              # in one terminal (fresh start, model warm)
    python load_report.py        # in another

Two parts, every number read back from logs/requests.jsonl by X-Request-ID:

1. **Latency breakdown.** 10 sequential POST /submit of the fixed 234-word
   text from measure_cost.py. Reports each stage's share of the server's
   wall time (stages_ms), signal one split into queue wait vs gpt2 compute
   (model_queue_ms / model_compute_ms), and the time no stage accounts for.

2. **Load observation.** Open-loop phases, 60 s each, every request sent on
   schedule whether or not earlier ones have finished:

     normal       1 writer at the rate limit: 12/min (0.2/s)    12 requests
     10x          10 writers, each at the limit: 2/s            120 requests
     10x-one      1 writer at 2/s (the rate limiter's case)     120 requests

Writes results/latency_load_<date>.md and a JSON file with every record.
"""

import argparse
import datetime as dt
import json
import statistics
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import config
import instrumentation
from measure_cost import RUN_TEXT

STAGES = ["validate", "signal_one", "signal_two", "combine", "label", "audit_write"]


def pct(values, p):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    k = (len(vals) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(vals) - 1)
    return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)


def mean(values):
    vals = [v for v in values if v is not None]
    return statistics.mean(vals) if vals else None


def fmt(x, nd=1):
    return "—" if x is None else f"{x:,.{nd}f}"


def send(session_factory, base, creator, tag):
    rid = f"{tag}-{uuid.uuid4().hex[:8]}"
    t0 = time.perf_counter()
    try:
        r = session_factory().post(f"{base}/submit",
                                   json={"text": RUN_TEXT, "creator_id": creator},
                                   headers={"X-Request-ID": rid}, timeout=600)
        status = r.status_code
    except Exception as exc:  # noqa: BLE001
        status = f"client error: {type(exc).__name__}"
    return {"request_id": rid, "creator": creator, "status": status,
            "client_ms": (time.perf_counter() - t0) * 1000}


def records_by_id(ids, wait_s=3.0):
    wanted = set(ids)
    deadline = time.time() + wait_s
    while True:
        found = {r["request_id"]: r for r in instrumentation.read_requests()
                 if r.get("request_id") in wanted}
        if len(found) == len(wanted) or time.time() > deadline:
            return found
        time.sleep(0.3)


# ── Part 1 ──────────────────────────────────────────────────────────────────

def breakdown(base, runs, session_factory):
    print(f"Latency breakdown: {runs} sequential runs…")
    sent = []
    for i in range(runs):
        res = send(session_factory, base, f"lat_{uuid.uuid4().hex[:6]}", "lat")
        sent.append(res)
        print(f"  run {i + 1:>2}: {res['status']}  {res['client_ms']:7.1f} ms")
    recs = records_by_id([s["request_id"] for s in sent])
    rows = []
    for s in sent:
        r = recs.get(s["request_id"])
        if not r or r.get("status") != 200:
            continue
        st = r.get("stages_ms", {})
        timed = sum(st.get(k, 0.0) for k in STAGES)
        rows.append({
            "client_ms": s["client_ms"],
            "duration_ms": r["duration_ms"],
            **{k: st.get(k) for k in STAGES},
            "model_queue_ms": r.get("model_queue_ms"),
            "model_compute_ms": r.get("model_compute_ms"),
            "untimed_ms": r["duration_ms"] - timed,
            "network_ms": s["client_ms"] - r["duration_ms"],
        })
    return rows


# ── Part 2 ──────────────────────────────────────────────────────────────────

def load_phase(base, name, rate_per_s, seconds, creators, session_factory):
    n = int(rate_per_s * seconds)
    interval = 1.0 / rate_per_s
    print(f"Load phase '{name}': {n} requests at {rate_per_s}/s "
          f"over {seconds} s from {len(creators)} writer(s)…")
    results = [None] * n
    with ThreadPoolExecutor(max_workers=n) as pool:
        start = time.perf_counter()
        futures = []
        for i in range(n):
            delay = start + i * interval - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
            send_at = time.perf_counter() - start
            creator = creators[i % len(creators)]

            def job(i=i, send_at=send_at, creator=creator):
                res = send(session_factory, base, creator, f"load-{name}")
                res["sent_at_s"] = send_at
                res["done_at_s"] = time.perf_counter() - start
                results[i] = res
            futures.append(pool.submit(job))
        for f in futures:
            f.result()
        wall = time.perf_counter() - start
    recs = records_by_id([r["request_id"] for r in results])
    for res in results:
        rec = recs.get(res["request_id"]) or {}
        res["record"] = {k: rec.get(k) for k in
                         ("status", "duration_ms", "cpu_ms", "rss_mb",
                          "model_queue_ms", "model_compute_ms", "stages_ms")}
    print(f"  finished in {wall:.1f} s")
    return {"name": name, "rate_per_s": rate_per_s, "seconds": seconds,
            "writers": len(creators), "wall_s": wall, "results": results}


def summarise(phase):
    res = phase["results"]
    ok = [r for r in res if r["status"] == 200]
    statuses = {}
    for r in res:
        statuses[str(r["status"])] = statuses.get(str(r["status"]), 0) + 1
    rec_ok = [r["record"] for r in ok]
    last_done = max((r["done_at_s"] for r in ok), default=None)
    # Throughput while saturated: completions per second between the first
    # and last 200 to finish.
    dones = sorted(r["done_at_s"] for r in ok)
    tput = (len(dones) - 1) / (dones[-1] - dones[0]) if len(dones) > 1 else None
    rss = [r["rss_mb"] for r in rec_ok if r.get("rss_mb")]
    # Time order: how the wait grew across the phase.
    ordered = sorted(ok, key=lambda r: r["sent_at_s"])
    thirds = []
    for j in range(3):
        part = ordered[j * len(ordered) // 3:(j + 1) * len(ordered) // 3]
        thirds.append(mean([r["client_ms"] for r in part]))
    return {
        "statuses": statuses,
        "ok": len(ok),
        "client_p50": pct([r["client_ms"] for r in ok], 50),
        "client_p95": pct([r["client_ms"] for r in ok], 95),
        "client_max": max((r["client_ms"] for r in ok), default=None),
        "queue_mean": mean([r.get("model_queue_ms") for r in rec_ok]),
        "queue_max": max((r.get("model_queue_ms") or 0 for r in rec_ok), default=None),
        "compute_mean": mean([r.get("model_compute_ms") for r in rec_ok]),
        "compute_p95": pct([r.get("model_compute_ms") for r in rec_ok], 95),
        "rss_peak": max(rss) if rss else None,
        "rss_last": rss[-1] if rss else None,
        "throughput": tput,
        "last_done_s": last_done,
        "thirds": thirds,
        "rejected_ms_p50": pct([r["client_ms"] for r in res if r["status"] == 429], 50),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--base", default=f"http://127.0.0.1:{config.PORT}")
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--normal-rate", type=float, default=config.RATE_LIMIT_PER_MINUTE / 60)
    args = ap.parse_args()

    import requests

    # The Windows console is cp1252; the report uses ↳ and ×.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    local = threading.local()

    def session_factory():
        if not hasattr(local, "s"):
            local.s = requests.Session()
        return local.s

    try:
        health = requests.get(f"{args.base}/health", timeout=5).json()
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"Service isn't answering at {args.base} ({exc}). Start it: python serve.py")
    if not health.get("detector_loaded"):
        sys.exit("Model isn't loaded. Start the service with `python serve.py`.")

    rows = breakdown(args.base, args.runs, session_factory)

    tag = uuid.uuid4().hex[:4]
    normal = load_phase(args.base, "normal", args.normal_rate, args.seconds,
                        [f"load_{tag}_n"], session_factory)
    print("  (pausing 20 s so the queue drains)")
    time.sleep(20)
    tenx = load_phase(args.base, "10x", args.normal_rate * 10, args.seconds,
                      [f"load_{tag}_w{i}" for i in range(10)], session_factory)
    print("  (pausing 20 s)")
    time.sleep(20)
    one = load_phase(args.base, "10x-one", args.normal_rate * 10, args.seconds,
                     [f"load_{tag}_solo"], session_factory)

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    out = Path("results") / f"latency_load_{stamp}.md"
    raw = Path("results") / f"latency_load_{stamp}.json"
    raw.write_text(json.dumps({"breakdown": rows, "phases": [normal, tenx, one]},
                              indent=1), encoding="utf-8")

    L = [f"# Latency breakdown and load observation — {stamp}", "",
         "Produced by `load_report.py` against `serve.py`. Every server-side "
         "number is read back from `logs/requests.jsonl` by X-Request-ID.", "",
         f"## 1. Latency breakdown — {len(rows)} sequential runs, 234-word text", "",
         "| Part of the run | Mean ms | p95 ms | Share of server wall |",
         "|---|---|---|---|"]
    dur = mean([r["duration_ms"] for r in rows])
    parts = [("validate", "validate"),
             ("signal_one (total)", "signal_one"),
             ("↳ queue wait for model thread", "model_queue_ms"),
             ("↳ gpt2 compute", "model_compute_ms"),
             ("signal_two (stylometry)", "signal_two"),
             ("combine", "combine"), ("label", "label"),
             ("audit_write", "audit_write"),
             ("not in any stage (token recount, Flask, hooks)", "untimed_ms")]
    for label, key in parts:
        m = mean([r.get(key) for r in rows])
        L.append(f"| {label} | {fmt(m, 2)} | {fmt(pct([r.get(key) for r in rows], 95), 2)} "
                 f"| {fmt(100 * m / dur if m is not None else None, 2)}% |")
    L.append(f"| **Server wall time (`duration_ms`)** | **{fmt(dur, 1)}** | "
             f"{fmt(pct([r['duration_ms'] for r in rows], 95), 1)} | 100% |")
    L.append(f"| Client-side extra (HTTP + JSON) | {fmt(mean([r['network_ms'] for r in rows]), 2)} "
             f"| | |")
    L += ["", "## 2. Load observation", "",
          "| | Normal | 10× (10 writers) | 10× (one writer) |", "|---|---|---|---|"]
    phases = [normal, tenx, one]
    S = [summarise(p) for p in phases]
    def row(label, fn):
        L.append(f"| {label} | " + " | ".join(fn(p, s) for p, s in zip(phases, S)) + " |")
    row("Offered rate", lambda p, s: f"{p['rate_per_s']:.2f}/s ({len(p['results'])} in {p['seconds']} s)")
    row("Status codes", lambda p, s: ", ".join(f"{v}×{k}" for k, v in sorted(s["statuses"].items())))
    row("Client latency p50 (200s)", lambda p, s: f"{fmt(s['client_p50'], 0)} ms")
    row("Client latency p95", lambda p, s: f"{fmt(s['client_p95'], 0)} ms")
    row("Client latency max", lambda p, s: f"{fmt(s['client_max'], 0)} ms")
    row("Mean latency, 1st / 2nd / 3rd of phase", lambda p, s: " / ".join(fmt(t, 0) for t in s["thirds"]) + " ms")
    row("Queue wait for model, mean / max", lambda p, s: f"{fmt(s['queue_mean'], 0)} / {fmt(s['queue_max'], 0)} ms")
    row("gpt2 compute, mean / p95", lambda p, s: f"{fmt(s['compute_mean'], 0)} / {fmt(s['compute_p95'], 0)} ms")
    row("Completed throughput", lambda p, s: f"{fmt(s['throughput'], 2)}/s")
    row("Last 200 finished at", lambda p, s: f"{fmt(s['last_done_s'], 1)} s")
    row("429 latency p50", lambda p, s: f"{fmt(s['rejected_ms_p50'], 0)} ms")
    row("RSS peak / at end", lambda p, s: f"{fmt(s['rss_peak'], 0)} / {fmt(s['rss_last'], 0)} MB")
    L += ["", f"Raw data: `{raw.as_posix()}`", ""]
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
