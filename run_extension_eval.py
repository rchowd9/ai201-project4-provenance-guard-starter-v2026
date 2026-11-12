#!/usr/bin/env python3
"""
Run the five Shape A extension criteria (criteria.md, "Extension criteria").

    python run_extension_eval.py --trial 1
    python run_extension_eval.py --trial 2
    python run_extension_eval.py --trial 3
    python run_extension_eval.py --summarize      # builds the run log table

Each trial is self-contained. It starts its OWN fresh server processes on
ports 5101–5105, so nothing carries over from a previous trial (criterion 4
needs a freshly started service). Don't have another copy running on those
ports.

What each trial runs, and what it produces:

  Phase A — fresh `serve.py` (port 5101)
    C4, C3  10 sequential runs of the fixed 234-word text (measure_cost.RUN_TEXT),
            sent as the first submissions after startup.
    C5      100 sequential submissions (perf_report.PROBE_TEXTS), one creator
            each; RSS read from each request's record.
    C1      60 mixed requests, each with its own X-Request-ID: 30 valid,
            the 12 malformed rows (RQ01–RQ12) from the attack set, 15 from one
            creator (expect ≥3 × 429), 2 appeals on real content_ids and 1 on
            an unknown one. Then every id is looked up in logs/requests.jsonl.

  Phase B — failures, triggered deliberately (C2)
    a  `serve.py` with AI201_INJECT_FAULT=signal_two        (port 5102)
    b  Flask debug mode (`flask --app app run --debug --no-reload`, the same
       exception propagation as `python app.py`) with the same fault (5103)
    c  `flask --app app run` with AI201_DETECTOR_MODEL set to a model that
       doesn't exist, then one /submit, timed                (port 5104)
    d  `serve.py` with that same bad model: must exit without opening the port
                                                             (port 5105)

Every number is read back from the service's own records in
logs/requests.jsonl by request id. Raw output — server stdout/stderr and the
full trial result — goes to results/ext_eval/.
"""

import argparse
import csv
import datetime as dt
import json
import os
import statistics
import subprocess
import sys
import time
import uuid
from pathlib import Path

import config
import instrumentation
from measure_cost import RUN_TEXT
from perf_report import PROBE_TEXTS

PY = sys.executable
OUT_DIR = config.RESULTS_DIR / "ext_eval"
MALFORMED_CSV = config.ROOT / "attack_set" / "attack_set" / "attacks_malformed_requests.csv"
BAD_MODEL = "provenance-guard/no-such-model-xyz"

# ── targets, exactly as written in criteria.md ───────────────────────────────
C2_503_LIMIT_S = 30.0
C3_CPU_LIMIT_S = 5.0
C3_WALL_LIMIT_S = 1.5
C4_RATIO_LIMIT = 1.5
C5_PEAK_LIMIT_MB = 1536.0
C5_CREEP_LIMIT_MB = 100.0


# ── process helpers ──────────────────────────────────────────────────────────

class Server:
    def __init__(self, name, args, port, env_extra, trial):
        self.name, self.port = name, port
        self.log_path = OUT_DIR / f"trial{trial}_{name}.log"
        env = os.environ.copy()
        env.update({"PORT": str(port), "HOST": "127.0.0.1",
                    "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"})
        env.update(env_extra)
        self.started = time.time()
        self.started_iso = instrumentation._now()
        self._log = self.log_path.open("w", encoding="utf-8")
        self.proc = subprocess.Popen(args, cwd=config.ROOT, env=env,
                                     stdout=self._log, stderr=subprocess.STDOUT)
        self.base = f"http://127.0.0.1:{port}"

    def port_open(self, session):
        try:
            session.get(f"{self.base}/health", timeout=2)
            return True
        except Exception:  # noqa: BLE001
            return False

    def wait_ready(self, session, timeout=180):
        end = time.time() + timeout
        while time.time() < end:
            if self.proc.poll() is not None:
                return False
            if self.port_open(session):
                return True
            time.sleep(0.5)
        return False

    def stop(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self._log.close()


def _rid(tag):
    return f"ext-{tag}-{uuid.uuid4().hex[:8]}"


def _records(ids):
    """Every record for each id (a list, so duplicates show)."""
    wanted = set(ids)
    found = {i: [] for i in ids}
    for r in instrumentation.read_requests():
        if r.get("request_id") in wanted:
            found[r["request_id"]].append(r)
    return found


def _pct(values, p):
    data = sorted(values)
    k = max(0, min(len(data) - 1, -(-p * len(data) // 100) - 1))
    return data[int(k)]


# ── Phase A: one fresh serve.py ──────────────────────────────────────────────

def phase_a(trial, session):
    srv = Server("serve", [PY, "serve.py"], 5101, {}, trial)
    try:
        if not srv.wait_ready(session):
            raise SystemExit(f"serve.py didn't come up — see {srv.log_path}")
        out = {}

        # C4 + C3: the first 10 submissions after startup.
        ids, client = [], []
        for i in range(10):
            rid = _rid(f"t{trial}-c3")
            t = time.perf_counter()
            r = session.post(f"{srv.base}/submit", headers={"X-Request-ID": rid},
                             json={"text": RUN_TEXT, "creator_id": f"ext_t{trial}_c3_{i:02d}"},
                             timeout=180)
            client.append(round((time.perf_counter() - t) * 1000, 2))
            ids.append(rid)
            assert r.status_code == 200, f"C3 run {i + 1} got {r.status_code}"
        time.sleep(0.3)
        recs = [_records(ids)[i][0] for i in ids]
        runs = [{"request_id": r["request_id"], "wall_ms": r["duration_ms"],
                 "cpu_ms": r["cpu_ms"], "signal_one_ms": r["stages_ms"].get("signal_one"),
                 "tokens": r.get("model_tokens"), "rss_mb": r.get("rss_mb"),
                 "client_ms": c} for r, c in zip(recs, client)]
        walls = [x["wall_ms"] for x in runs]
        cpus = [x["cpu_ms"] for x in runs]
        median_rest = statistics.median(walls[1:])
        out["c3"] = {
            "runs": runs,
            "mean_cpu_s": round(statistics.mean(cpus) / 1000, 3),
            "sd_cpu_s": round(statistics.stdev(cpus) / 1000, 3),
            "mean_wall_s": round(statistics.mean(walls) / 1000, 3),
            "sd_wall_s": round(statistics.stdev(walls) / 1000, 3),
            "p50_wall_s": round(_pct(walls, 50) / 1000, 3),
            "p95_wall_s": round(_pct(walls, 95) / 1000, 3),
            "max_wall_s": round(max(walls) / 1000, 3),
        }
        out["c3"]["pass"] = (out["c3"]["mean_cpu_s"] <= C3_CPU_LIMIT_S
                             and out["c3"]["mean_wall_s"] <= C3_WALL_LIMIT_S)
        out["c4"] = {
            "run1_wall_s": round(walls[0] / 1000, 3),
            "median_runs_2_10_s": round(median_rest / 1000, 3),
            "ratio": round(walls[0] / median_rest, 3),
        }
        out["c4"]["pass"] = out["c4"]["ratio"] <= C4_RATIO_LIMIT
        print(f"  C3  mean CPU {out['c3']['mean_cpu_s']} s, mean wall {out['c3']['mean_wall_s']} s")
        print(f"  C4  run 1 {out['c4']['run1_wall_s']} s = {out['c4']['ratio']}× median")

        # C5: 100 sequential submissions, RSS from each record.
        ids = []
        for i in range(100):
            rid = _rid(f"t{trial}-c5")
            r = session.post(f"{srv.base}/submit", headers={"X-Request-ID": rid},
                             json={"text": PROBE_TEXTS[i % len(PROBE_TEXTS)],
                                   "creator_id": f"ext_t{trial}_c5_{i:03d}"}, timeout=180)
            ids.append(rid)
        time.sleep(0.3)
        found = _records(ids)
        rss = [found[i][0].get("rss_mb") for i in ids]
        walls5 = [found[i][0]["duration_ms"] for i in ids]
        statuses5 = [found[i][0]["status"] for i in ids]
        early, late = statistics.mean(rss[10:20]), statistics.mean(rss[-10:])
        out["c5"] = {
            "peak_rss_mb": max(rss),
            "first_rss_mb": rss[0],
            "mean_rss_req_11_20": round(early, 1),
            "mean_rss_last_10": round(late, 1),
            "creep_mb": round(late - early, 1),
            "rss_series": rss,
            "statuses": {str(s): statuses5.count(s) for s in set(statuses5)},
            "latency_ms": {"p50": _pct(walls5, 50), "p95": _pct(walls5, 95),
                           "max": max(walls5)},
        }
        out["c5"]["pass"] = (out["c5"]["peak_rss_mb"] <= C5_PEAK_LIMIT_MB
                             and out["c5"]["creep_mb"] <= C5_CREEP_LIMIT_MB)
        print(f"  C5  peak {out['c5']['peak_rss_mb']} MB, creep {out['c5']['creep_mb']:+} MB")

        # C1: 60 mixed requests, every id must appear exactly once.
        sent = []  # (rid, kind, client_status)

        def post(kind, rid, path, **kw):
            headers = {"X-Request-ID": rid, **kw.pop("headers", {})}
            r = session.post(f"{srv.base}{path}", headers=headers, timeout=180, **kw)
            sent.append((rid, kind, r.status_code))
            return r

        content_ids = []
        for i in range(30):
            r = post("valid", _rid(f"t{trial}-c1v"), "/submit",
                     json={"text": PROBE_TEXTS[i % len(PROBE_TEXTS)],
                           "creator_id": f"ext_t{trial}_c1_{i:02d}"})
            if r.ok:
                content_ids.append(r.json()["content_id"])
        with MALFORMED_CSV.open(encoding="utf-8", newline="") as f:
            rows = [row for row in csv.DictReader(f) if row["id"].startswith("RQ")]
        for row in rows:
            rid = _rid(f"t{trial}-c1m-{row['id']}")
            if row["send_as"] == "raw":
                post(f"malformed {row['id']}", rid, "/submit",
                     data=row["raw_body"].encode("utf-8"),
                     headers={"Content-Type": row["content_type"] or "application/json"})
            else:
                post(f"malformed {row['id']}", rid, "/submit", json=json.loads(row["raw_body"]))
        flood_creator = f"ext_t{trial}_flood"
        for i in range(15):
            post("flood", _rid(f"t{trial}-c1f"), "/submit",
                 json={"text": PROBE_TEXTS[0], "creator_id": flood_creator})
        for cid in content_ids[:2]:
            post("appeal", _rid(f"t{trial}-c1a"), "/appeal",
                 json={"content_id": cid, "reasoning": "Extension eval: exercising the appeal path."})
        post("appeal unknown", _rid(f"t{trial}-c1a"), "/appeal",
             json={"content_id": "no-such-content-id", "reasoning": "Extension eval: unknown id."})
        time.sleep(0.5)

        found = _records([s[0] for s in sent])
        missing = [s for s in sent if len(found[s[0]]) == 0]
        dups = [s for s in sent if len(found[s[0]]) > 1]
        mismatched, incomplete = [], []
        for rid, kind, status in sent:
            for rec in found[rid][:1]:
                if rec.get("status") != status:
                    mismatched.append((rid, kind, status, rec.get("status")))
                if not (rec.get("timestamp") and rec.get("outcome")
                        and rec.get("duration_ms") is not None
                        and rec.get("input") and rec.get("output")):
                    incomplete.append((rid, kind))
        codes = [s[2] for s in sent]
        out["c1"] = {
            "sent": len(sent),
            "logged_once": sum(1 for s in sent if len(found[s[0]]) == 1),
            "missing": missing, "duplicated": dups,
            "status_mismatch": mismatched, "incomplete": incomplete,
            "status_counts": {str(c): codes.count(c) for c in sorted(set(codes))},
            "n_429": codes.count(429),
            "by_kind": [{"kind": k, "status": s, "outcome": (found[r][0].get("outcome") if found[r] else None)}
                        for r, k, s in sent if k != "valid"],
        }
        out["c1"]["pass"] = (len(sent) == 60 and out["c1"]["logged_once"] == 60
                             and not mismatched and not incomplete and out["c1"]["n_429"] >= 3)
        print(f"  C1  {out['c1']['logged_once']}/{len(sent)} logged once, "
              f"{len(missing)} missing, {len(dups)} dup, {codes.count(429)}×429, "
              f"status codes {out['c1']['status_counts']}")
        return out
    finally:
        srv.stop()


# ── Phase B: failures, on purpose ────────────────────────────────────────────

def _crash_case(trial, session, name, args, port, env):
    srv = Server(name, args, port, env, trial)
    try:
        if not srv.wait_ready(session):
            return {"pass": False, "note": f"server didn't start, see {srv.log_path.name}"}
        rid = _rid(f"t{trial}-{name}")
        t = time.perf_counter()
        r = session.post(f"{srv.base}/submit", headers={"X-Request-ID": rid},
                         json={"text": RUN_TEXT, "creator_id": f"ext_t{trial}_{name}"},
                         timeout=300)
        elapsed = round(time.perf_counter() - t, 2)
        time.sleep(0.5)
        recs = _records([rid])[rid]
        rec = recs[0] if recs else {}
        exc = rec.get("exception") or {}
        res = {
            "client_status": r.status_code,
            "client_content_type": r.headers.get("Content-Type"),
            "client_s": elapsed,
            "records": len(recs),
            "outcome": rec.get("outcome"),
            "exception_type": exc.get("type"),
            "exception_message": exc.get("message"),
            "failed_stage": rec.get("failed_stage"),
        }
        return res
    finally:
        srv.stop()


def phase_b(trial, session):
    out = {}

    # a: mid-request crash under serve.py
    a = _crash_case(trial, session, "crash_serve", [PY, "serve.py"], 5102,
                    {"AI201_INJECT_FAULT": "signal_two"})
    a["pass"] = (a.get("records") == 1 and a.get("outcome") == "error"
                 and a.get("exception_type") == "InjectedFault"
                 and a.get("failed_stage") == "signal_two")
    out["a_crash_serve"] = a

    # b: mid-request crash under Flask debug mode (exception propagates)
    b = _crash_case(trial, session, "crash_debug",
                    [PY, "-m", "flask", "--app", "app", "run", "--debug", "--no-reload",
                     "--port", "5103"], 5103, {"AI201_INJECT_FAULT": "signal_two"})
    b["pass"] = (b.get("records") == 1 and b.get("outcome") == "error"
                 and b.get("exception_type") == "InjectedFault"
                 and b.get("failed_stage") == "signal_two")
    out["b_crash_debug"] = b

    # c: model can't load, /submit must answer a JSON 503 within 30 s
    c = _crash_case(trial, session, "bad_model_submit",
                    [PY, "-m", "flask", "--app", "app", "run", "--no-reload", "--port", "5104"],
                    5104, {"AI201_DETECTOR_MODEL": BAD_MODEL})
    c["pass"] = (c.get("client_status") == 503
                 and "json" in (c.get("client_content_type") or "")
                 and c.get("client_s", 999) <= C2_503_LIMIT_S
                 and c.get("records") == 1 and c.get("outcome") == "error"
                 and bool(c.get("exception_type")))
    out["c_bad_model_submit"] = c

    # d: serve.py with the bad model must not open the port and must log why
    srv = Server("bad_model_start", [PY, "serve.py"], 5105, {"AI201_DETECTOR_MODEL": BAD_MODEL}, trial)
    port_ever_open = False
    try:
        end = time.time() + 120
        while time.time() < end and srv.proc.poll() is None:
            port_ever_open = port_ever_open or srv.port_open(session)
            time.sleep(0.5)
        exited = srv.proc.poll() is not None
        exit_code = srv.proc.returncode
        elapsed = round(time.time() - srv.started, 2)
    finally:
        srv.stop()
    startups = [r for r in instrumentation.read_requests()
                if r.get("event") == "startup" and r.get("outcome") == "error"
                and r.get("timestamp", "") >= srv.started_iso
                and r.get("model") == BAD_MODEL]
    d = {
        "exited": exited, "exit_code": exit_code, "seconds_to_exit": elapsed,
        "port_ever_open": port_ever_open, "startup_error_records": len(startups),
        "exception_type": (startups[0].get("exception") or {}).get("type") if startups else None,
    }
    d["pass"] = exited and exit_code != 0 and not port_ever_open and len(startups) == 1
    out["d_bad_model_start"] = d

    out["pass"] = all(v["pass"] for v in out.values() if isinstance(v, dict))
    out["cases_passed"] = sum(1 for v in out.values() if isinstance(v, dict) and v["pass"])
    for k, v in out.items():
        if isinstance(v, dict):
            print(f"  C2{k[0]} {'PASS' if v['pass'] else 'FAIL'}  "
                  + json.dumps({x: y for x, y in v.items() if x != 'pass'}))
    return out


# ── Summary ──────────────────────────────────────────────────────────────────

def summarize():
    trials = {}
    for n in (1, 2, 3):
        files = sorted(OUT_DIR.glob(f"trial{n}_result_*.json"))
        if files:
            trials[n] = json.loads(files[-1].read_text(encoding="utf-8"))
    if len(trials) < 3:
        sys.exit(f"Need 3 trials, found {sorted(trials)}. Run --trial 1/2/3 first.")

    def cell(n, key):
        t = trials[n]
        if key == "c1":
            c = t["c1"]
            return (f"{c['logged_once']}/{c['sent']} logged once, {len(c['missing'])} missing, "
                    f"{len(c['duplicated'])} dup, {len(c['status_mismatch'])} status mismatch, "
                    f"{c['n_429']}×429")
        if key == "c2":
            c = t["c2"]
            return (f"{c['cases_passed']}/4 cases; 503 JSON in "
                    f"{c['c_bad_model_submit'].get('client_s')} s; bad start exit "
                    f"{c['d_bad_model_start']['exit_code']}, port opened: "
                    f"{'yes' if c['d_bad_model_start']['port_ever_open'] else 'no'}")
        if key == "c3":
            c = t["c3"]
            return f"CPU {c['mean_cpu_s']:.2f} s, wall {c['mean_wall_s']:.2f} s (p95 {c['p95_wall_s']:.2f})"
        if key == "c4":
            c = t["c4"]
            return f"run 1 {c['run1_wall_s']:.2f} s vs median {c['median_runs_2_10_s']:.2f} s = {c['ratio']:.2f}×"
        if key == "c5":
            c = t["c5"]
            return f"peak {c['peak_rss_mb']:,.0f} MB, creep {c['creep_mb']:+.0f} MB"

    rows = [
        ("1. Every request leaves exactly one record",
         "60/60 ids logged exactly once, statuses match, ≥3×429", "c1"),
        ("2. Failures get an answer and leave their cause",
         "4/4 forced failures recorded with exception; 503 JSON ≤ 30 s; bad start doesn't open port", "c2"),
        ("3. Cost of one run", "mean ≤ 5.0 CPU-s and ≤ 1.5 s wall (10 runs)", "c3"),
        ("4. No first-request penalty", "run 1 ≤ 1.5× median of runs 2–10", "c4"),
        ("5. Memory within requirement, no creep",
         "peak ≤ 1,536 MB; last-10 mean ≤ +100 MB vs requests 11–20", "c5"),
    ]
    L = [f"# Extension run log — {dt.datetime.now():%Y-%m-%d %H:%M}", "",
         "Produced by `run_extension_eval.py`; three separate invocations "
         "(`--trial 1/2/3`), each with fresh server processes.", "",
         "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |", "|---|---|---|---|---|---|"]
    for name, target, key in rows:
        passes = [trials[n][key]["pass"] for n in (1, 2, 3)]
        verdict = "**MET** (3 of 3 trials)" if all(passes) else f"**MISSED** (failed in {passes.count(False)} of 3 trials)"
        L.append(f"| {name} | {target} | " + " | ".join(
            cell(n, key) + ("" if trials[n][key]["pass"] else " ✗") for n in (1, 2, 3))
            + f" | {verdict} |")
    L += ["", "Trial files: " + ", ".join(f"`{trials[n]['_file']}`" for n in (1, 2, 3)), ""]
    report = "\n".join(L)
    out = config.RESULTS_DIR / f"ext_eval_{dt.datetime.now():%Y-%m-%d_%H%M}.md"
    out.write_text(report + "\n", encoding="utf-8")
    print(report)
    print(f"\nWrote {out.relative_to(config.ROOT)}")


def main():
    ap = argparse.ArgumentParser(description="Shape A extension criteria, one trial at a time.")
    ap.add_argument("--trial", type=int, choices=[1, 2, 3])
    ap.add_argument("--summarize", action="store_true")
    args = ap.parse_args()
    if args.summarize:
        return summarize()
    if not args.trial:
        ap.error("give --trial N or --summarize")

    import requests

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    started = dt.datetime.now()
    print(f"Trial {args.trial} — {started:%Y-%m-%d %H:%M:%S}")
    print("Phase A: fresh serve.py (C3, C4, C5, C1)")
    result = phase_a(args.trial, session)
    print("Phase B: deliberate failures (C2)")
    result["c2"] = phase_b(args.trial, session)
    result["trial"] = args.trial
    result["started"] = started.isoformat(timespec="seconds")
    result["finished"] = dt.datetime.now().isoformat(timespec="seconds")
    path = OUT_DIR / f"trial{args.trial}_result_{started:%Y-%m-%d_%H%M%S}.json"
    result["_file"] = str(path.relative_to(config.ROOT)).replace("\\", "/")
    path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print("Verdicts this trial: " + ", ".join(
        f"C{k[1]} {'pass' if result[k]['pass'] else 'MISS'}" for k in ("c1", "c2", "c3", "c4", "c5")))
    print(f"Wrote {result['_file']}")


if __name__ == "__main__":
    main()
