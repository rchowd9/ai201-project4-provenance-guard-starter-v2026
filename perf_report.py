#!/usr/bin/env python3
"""
Live performance numbers for the running service — Shape A.

    python serve.py                       # in one terminal
    python perf_report.py --probe 20      # in another: send 20, then report

    python perf_report.py                 # report on everything in the log
    python perf_report.py --since 2026-11-07T18:00

Reads logs/requests.jsonl (written by instrumentation.py on every request) and
writes results/perf_<date>.md: status codes per route, latency percentiles,
where the time goes inside /submit, cold-start cost, and memory against the
512 MB a free host gives you.

`--probe N` sends N real submissions first, each under its own creator_id
(`perf_probe_<n>`) so the rate limiter doesn't turn a latency test into a
rate-limit test, then one deliberately bad request and one /appeal, so every
code path shows up in the numbers. The probe texts are fixed so runs compare.
"""

import argparse
import datetime as dt
import json
import sys
import time

import config
import instrumentation

PROBE_TEXTS = [
    # short, plain human note
    "Hey, just grabbed some coffee and was looking over the git logs we talked "
    "about earlier. Let me know if you want to sync up later this afternoon to "
    "review the remaining issues.",
    # generic AI-style paragraph
    "Artificial intelligence is transforming the way organizations operate. By "
    "automating routine tasks, it allows employees to focus on higher-value work. "
    "Furthermore, it enables data-driven decision making across every department. "
    "As a result, companies that embrace these tools are well positioned for the future.",
    # longer, uneven human prose (Thoreau, Walden, 1854 — public domain)
    "When I wrote the following pages, or rather the bulk of them, I lived alone, "
    "in the woods, a mile from any neighbor, in a house which I had built myself, "
    "on the shore of Walden Pond, in Concord, Massachusetts, and earned my living "
    "by the labor of my hands only. I lived there two years and two months. At "
    "present I am a sojourner in civilized life again.",
]


def _post(session, base, path, body):
    start = time.perf_counter()
    try:
        r = session.post(f"{base}{path}", json=body, timeout=180)
        return r, (time.perf_counter() - start) * 1000
    except Exception as exc:  # noqa: BLE001
        print(f"  {path}: request failed — {exc}")
        return None, (time.perf_counter() - start) * 1000


def probe(n: int, base: str) -> dict:
    import requests

    session = requests.Session()
    try:
        session.get(f"{base}/health", timeout=5).raise_for_status()
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"Service isn't answering at {base} ({exc}). Start it with: python serve.py")

    print(f"Probing {base} with {n} submissions…")
    client_ms, codes, content_id = [], [], None
    wall = time.perf_counter()
    for i in range(n):
        text = PROBE_TEXTS[i % len(PROBE_TEXTS)]
        r, ms = _post(session, base, "/submit",
                      {"text": text, "creator_id": f"perf_probe_{i:03d}"})
        client_ms.append(ms)
        codes.append(r.status_code if r is not None else "ERR")
        if r is not None and r.ok and content_id is None:
            content_id = r.json().get("content_id")
        print(f"  {i + 1:>3}/{n}  {codes[-1]}  {ms:7.0f} ms"
              + (f"  server: {r.headers.get('Server-Timing', '')}" if r is not None else ""))
    wall_s = time.perf_counter() - wall

    # One of each other path, so the report isn't only the happy path.
    r, _ = _post(session, base, "/submit", {"text": "", "creator_id": "perf_probe_bad"})
    print(f"  bad input  -> {r.status_code if r is not None else 'ERR'}")
    if content_id:
        r, _ = _post(session, base, "/appeal", {
            "content_id": content_id,
            "reasoning": "perf probe: exercising the appeal path, not a real dispute.",
        })
        print(f"  appeal     -> {r.status_code if r is not None else 'ERR'}")

    live = session.get(f"{base}/metrics", timeout=10).json()
    return {"n": n, "codes": codes, "client_ms": client_ms, "wall_s": wall_s, "live": live}


def _table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def build_report(rows: list[dict], probe_result: dict | None, since: str | None) -> str:
    pct = instrumentation.percentiles
    budget = instrumentation.FREE_TIER_MB
    startups = [r for r in rows if r.get("event") == "startup"]
    reqs = [r for r in rows if "route" in r]

    lines = [f"# Performance run — {dt.datetime.now():%Y-%m-%d %H:%M}", ""]
    lines.append(f"Source: `{config.REQUEST_LOG.relative_to(config.ROOT)}`"
                 + (f", entries since `{since}`" if since else ", whole log")
                 + f". {len(reqs)} requests, {len(startups)} startup event(s).")
    if reqs:
        lines.append(f"Window: {reqs[0]['timestamp']} → {reqs[-1]['timestamp']}.")
    lines.append("")

    # ── Startup
    lines += ["## Startup", ""]
    if startups:
        lines.append(_table(
            ["timestamp", "pid", "model", "model load (s)", "RSS before model (MB)", "RSS after model (MB)"],
            [[s["timestamp"], s.get("pid"), s.get("model"), s.get("model_load_s"),
              s.get("rss_mb_before_model"), s.get("rss_mb_after_model")] for s in startups[-5:]],
        ))
    else:
        lines.append("No warm-up recorded — the service was started with `python app.py`, "
                     "so the first /submit paid the model load (see Cold start below).")
    lines.append("")

    # ── Status codes
    lines += ["## Status codes", ""]
    counts: dict = {}
    for r in reqs:
        key = (r["method"], r["route"])
        counts.setdefault(key, {})
        counts[key][r["status"]] = counts[key].get(r["status"], 0) + 1
    all_codes = sorted({c for v in counts.values() for c in v})
    lines.append(_table(
        ["route"] + [str(c) for c in all_codes] + ["total"],
        [[f"{m} {route}"] + [v.get(c, 0) for c in all_codes] + [sum(v.values())]
         for (m, route), v in sorted(counts.items())],
    ))
    lines.append("")

    # ── Latency per route
    lines += ["## Latency by route (server-side, ms)", ""]
    by_route: dict = {}
    for r in reqs:
        by_route.setdefault(f"{r['method']} {r['route']}", []).append(r.get("duration_ms", r.get("total_ms")))
    lines.append(_table(
        ["route", "n", "p50", "p95", "p99", "max", "mean"],
        [[k, *(pct(v).get(x, "—") for x in ("count", "p50", "p95", "p99", "max", "mean"))]
         for k, v in sorted(by_route.items())],
    ))
    lines.append("")

    # ── /submit stages (successful, warm requests only — cold ones skew it)
    ok_submits = [r for r in reqs if r["route"] == "/submit" and r["status"] == 200]
    warm = [r for r in ok_submits if not r.get("cold_start")]
    lines += ["## Where the time goes in a /submit (200s, warm model, ms)", ""]
    if warm:
        stage_names = ["validate", "signal_one", "signal_two", "combine", "label", "audit_write"]
        totals = [r.get("duration_ms", r.get("total_ms")) for r in warm]
        mean_total = sum(totals) / len(totals)
        table = []
        for name in stage_names:
            vals = [r["stages_ms"].get(name, 0.0) for r in warm]
            p = pct(vals)
            share = 100 * p["mean"] / mean_total if mean_total else 0
            table.append([name, p["p50"], p["p95"], p["max"], p["mean"], f"{share:.1f}%"])
        overhead = [r.get("duration_ms", r.get("total_ms")) - sum(r["stages_ms"].values()) for r in warm]
        p = pct(overhead)
        table.append(["(framework + limiter)", p["p50"], p["p95"], p["max"], p["mean"],
                      f"{100 * p['mean'] / mean_total:.1f}%"])
        p = pct(totals)
        table.append(["**total**", p["p50"], p["p95"], p["max"], p["mean"], "100%"])
        lines.append(_table(["stage", "p50", "p95", "max", "mean", "share of mean"], table))
    else:
        lines.append("No successful warm /submit requests in this window.")
    lines.append("")

    # ── Cold start
    cold = [r for r in ok_submits if r.get("cold_start")]
    lines += ["## Cold start", ""]
    if cold:
        lines.append(_table(
            ["timestamp", "request_id", "total ms", "signal_one ms"],
            [[r["timestamp"], r["request_id"], r.get("duration_ms", r.get("total_ms")), r["stages_ms"].get("signal_one")]
             for r in cold],
        ))
        lines.append("")
        lines.append("These requests loaded the model inside the request. `serve.py` "
                     "moves that cost to startup.")
    else:
        lines.append("None — every successful /submit found the model already in memory.")
    lines.append("")

    # ── Memory
    rss = [r["rss_mb"] for r in reqs if r.get("rss_mb")] + \
          [s["rss_mb_after_model"] for s in startups if s.get("rss_mb_after_model")]
    lines += ["## Memory vs. a free host", ""]
    if rss:
        peak = max(rss)
        verdict = "does **not** fit" if peak > budget else "fits"
        lines.append(f"Peak resident memory seen: **{peak:.0f} MB**. A free tier gives "
                     f"**{budget} MB**, so this service {verdict} "
                     f"({peak - budget:+.0f} MB). That is why Shape A runs as Path B: "
                     "local, with these logs as the evidence.")
    else:
        lines.append("Memory couldn't be read on this platform.")
    lines.append("")

    # ── Probe
    if probe_result:
        cm = pct(probe_result["client_ms"])
        n = probe_result["n"]
        lines += ["## This probe", ""]
        lines.append(f"{n} sequential submissions in {probe_result['wall_s']:.1f} s "
                     f"→ **{n / probe_result['wall_s']:.2f} submissions/s** from one client.")
        lines.append("")
        lines.append("Status codes: " + " ".join(str(c) for c in probe_result["codes"]))
        lines.append("")
        lines.append(f"Client-side latency (includes network + JSON): p50 {cm['p50']} ms, "
                     f"p95 {cm['p95']} ms, max {cm['max']} ms.")
        lines.append("")
        lines.append("`GET /metrics` straight after the probe:")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(probe_result["live"], indent=2))
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--probe", type=int, default=0, metavar="N",
                    help="send N submissions to the running service first")
    ap.add_argument("--base", default=f"http://{'127.0.0.1' if config.HOST == '0.0.0.0' else config.HOST}:{config.PORT}")
    ap.add_argument("--since", help="only use log entries at or after this ISO timestamp")
    ap.add_argument("--no-write", action="store_true", help="print, don't write results/")
    args = ap.parse_args()

    since = args.since
    probe_result = None
    if args.probe:
        since = since or dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")
        probe_result = probe(args.probe, args.base)

    rows = instrumentation.read_requests()
    if since:
        # Keep the latest startup even if it was before the window: it's the
        # process the window ran against.
        startups = [r for r in rows if r.get("event") == "startup"]
        rows = [r for r in rows if r.get("timestamp", "") >= since]
        if startups and not any(r.get("event") == "startup" for r in rows):
            rows.insert(0, startups[-1])

    if not any("route" in r for r in rows):
        sys.exit(f"No requests in {config.REQUEST_LOG}"
                 + (f" since {since}" if since else "")
                 + ". Run the service and send it something, or use --probe N.")

    report = build_report(rows, probe_result, since)
    print()
    print(report)
    if not args.no_write:
        config.RESULTS_DIR.mkdir(exist_ok=True)
        out = config.RESULTS_DIR / f"perf_{dt.datetime.now():%Y-%m-%d_%H%M}.md"
        out.write_text(report + "\n", encoding="utf-8")
        print(f"\nWrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
