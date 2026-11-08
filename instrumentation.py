"""
Instrumentation — Shape A, "deploy and instrument".

The audit log (`audit.py`) answers *what did the service decide*. This module
answers *what did it cost to decide it*: how long each request took, where the
time went inside `/submit`, what status codes came back, and how much memory
the process is holding.

Three outputs, all from the same measurements:

    logs/requests.jsonl   one structured record per run (HTTP request), plus
                          a `startup` record per process. Append-only, like
                          the audit log, and joined to it by content_id.
    GET /metrics          a live snapshot of the counters below, from memory.
    response headers      X-Request-ID and Server-Timing on every response,
                          so a single curl -i shows the stage breakdown.

Every record has the same named fields:

    timestamp    UTC, milliseconds
    event        "request" or "startup"
    request_id   also returned as the X-Request-ID header
    method, route, status
    outcome      ok | rejected (4xx) | rate_limited (429) | error (5xx / crash)
    duration_ms  wall time of the whole run
    input        what was sent: creator_id, and for text/reasoning the length,
                 word count, a sha256 prefix and a 160-char preview. Wrong
                 types are named ("<int>"); an unparseable body keeps a preview
    output       what came back: content_id, guess, confidence, all three
                 scores, or the error message
    stages_ms    time per /submit stage (below)
    settings     model and thresholds in force, so an old record explains itself
    rss_mb, pid  memory and process
    exception    on a crash: type, message, last traceback frames
    failed_stage on a crash: which stage it died in
    cold_start, text_chars   when relevant

Failures are records, not gaps. A request that crashes still gets an
`outcome: "error"` record even under `python app.py`, where debug mode lets the
exception escape before after_request runs: teardown_request writes it. A
startup that can't load the model writes an `event: "startup"` error record.

Read it back:  python instrumentation.py --outcome error --json

The stages timed inside /submit match the five stages the README names, plus
the log write:

    validate → signal_one → signal_two → combine → label → audit_write

⚠️ The in-memory counters belong to one process. Under gunicorn with several
workers each worker has its own, so /metrics shows one worker's view. The
request log is shared by every worker, which is why `perf_report.py` builds its
numbers from the file rather than from /metrics.
"""

import hashlib
import json
import math
import os
import sys
import threading
import time
import traceback
import uuid
from collections import Counter, defaultdict, deque
from contextlib import contextmanager
from datetime import datetime, timezone

from flask import g, request

import config

# How many recent latencies to keep per route / stage for percentiles. Bounded
# so a long-running service doesn't grow without limit.
_WINDOW = 2000

_lock = threading.Lock()
_log_lock = threading.Lock()

_started_at = time.time()
_status_counts: Counter = Counter()           # (method, route, status) -> n
_route_ms: dict = defaultdict(lambda: deque(maxlen=_WINDOW))
_stage_ms: dict = defaultdict(lambda: deque(maxlen=_WINDOW))
_model_load_s: float | None = None
_peak_rss_mb: float = 0.0


# ── Memory ───────────────────────────────────────────────────────────────────

def rss_mb() -> float | None:
    """
    Resident memory of this process in MB, or None if it can't be read.

    This is the number that decides whether the service fits a host: a free
    tier gives 512 MB, and gpt2 plus torch is over that before any request.
    No extra dependency — psutil isn't in requirements.txt.
    """
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            class _PMC(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            counters = _PMC()
            counters.cb = ctypes.sizeof(_PMC)
            get_info = ctypes.windll.psapi.GetProcessMemoryInfo
            get_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PMC), wintypes.DWORD]
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            if get_info(handle, ctypes.byref(counters), counters.cb):
                return round(counters.WorkingSetSize / 1_048_576, 1)
            return None

        # Linux: current RSS from /proc. macOS / other Unix: peak RSS.
        if os.path.exists("/proc/self/status"):
            with open("/proc/self/status", encoding="ascii") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        return round(int(line.split()[1]) / 1024, 1)
        import resource

        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # ru_maxrss is bytes on macOS, kilobytes on Linux.
        return round(peak / (1_048_576 if sys.platform == "darwin" else 1024), 1)
    except Exception:  # noqa: BLE001 — a metric must never break a request
        return None


def _note_rss() -> float | None:
    global _peak_rss_mb
    current = rss_mb()
    if current is not None:
        with _lock:
            _peak_rss_mb = max(_peak_rss_mb, current)
    return current


# ── Stage timing ─────────────────────────────────────────────────────────────

@contextmanager
def stage(name: str):
    """
    Time one stage of the current request:

        with instrumentation.stage("signal_one"):
            model_score = detector.model_signal(text)

    The time is recorded even if the stage raises, so a stage that fails slowly
    still shows up as slow.
    """
    start = time.perf_counter()
    try:
        yield
    except BaseException:
        extra = getattr(g, "ops_extra", None)
        if extra is not None and "failed_stage" not in extra:
            extra["failed_stage"] = name   # where a crashed run died
        raise
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        stages = getattr(g, "stages", None)
        if stages is not None:
            stages[name] = round(stages.get(name, 0.0) + elapsed, 2)


def note(**fields):
    """Attach extra fields to this request's ops-log line (e.g. cold_start)."""
    extra = getattr(g, "ops_extra", None)
    if extra is not None:
        extra.update(fields)


# ── Model warm-up ────────────────────────────────────────────────────────────

def warm_up() -> dict:
    """
    Load the model before taking traffic, and time it.

    Without this the first real writer pays the 10–20 s load inside their
    request. With it, the cost is paid once at startup and shows up as a number
    instead of a mystery.
    """
    global _model_load_s
    import detector

    rss_before = rss_mb()
    start = time.perf_counter()
    first_pass_s = None
    try:
        detector.warm_up()
        load_s = time.perf_counter() - start
        # Loading isn't enough: torch does one-time setup on the first forward
        # pass (measured: a 6 s first run vs ~1 s after). Pay it here, on a
        # throwaway sentence, instead of inside the first writer's request.
        t_pass = time.perf_counter()
        detector.perplexity("The service is starting up and checking that the model runs.")
        first_pass_s = round(time.perf_counter() - t_pass, 2)
    except Exception as exc:
        # A service that couldn't start must leave a record too.
        _write({
            "timestamp": _now(),
            "event": "startup",
            "outcome": "error",
            "model": config.DETECTOR_MODEL,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            "exception": {
                "type": type(exc).__name__,
                "message": str(exc)[:500],
                "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__)[-6:],
            },
            "pid": os.getpid(),
        })
        raise
    _model_load_s = round(load_s, 2)
    rss_after = _note_rss()

    event = {
        "timestamp": _now(),
        "event": "startup",
        "outcome": "ok",
        "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        "model": config.DETECTOR_MODEL,
        "model_load_s": _model_load_s,
        "first_pass_s": first_pass_s,
        "rss_mb_before_model": rss_before,
        "rss_mb_after_model": rss_after,
        "pid": os.getpid(),
    }
    _write(event)
    return event


def record_cold_load(seconds: float):
    """A request that loaded the model itself (no warm-up) records it here."""
    global _model_load_s
    if _model_load_s is None:
        _model_load_s = round(seconds, 2)


# ── Flask wiring ─────────────────────────────────────────────────────────────

# How much of the submitted text a run record keeps. Enough to recognise the
# input when reading the log back; the full text is in the audit log for
# decisions. The hash identifies the exact input without storing it all.
INPUT_PREVIEW_CHARS = 160

# Response fields copied into a record's `output`. Labels are long and fixed
# per guess, so the guess stands in for them.
_OUTPUT_FIELDS = ("content_id", "guess", "confidence", "combined_score",
                  "model_score", "style_score", "status", "error", "message", "limit")


def _preview(text: str) -> str:
    return text if len(text) <= INPUT_PREVIEW_CHARS else text[:INPUT_PREVIEW_CHARS] + "…"


def _describe_input() -> dict:
    """What the caller sent, as named fields — readable later, never huge."""
    info = {
        "content_type": request.mimetype or None,
        "bytes": request.content_length,
    }
    if request.args:
        info["query"] = request.args.to_dict()

    payload = request.get_json(silent=True)  # cached; costs nothing after the route
    if isinstance(payload, dict):
        creator = payload.get("creator_id")
        info["creator_id"] = creator if isinstance(creator, str) else (
            None if creator is None else f"<{type(creator).__name__}>")
        for field in ("text", "reasoning", "message"):
            value = payload.get(field)
            if isinstance(value, str):
                info[field] = {
                    "chars": len(value),
                    "words": len(value.split()),
                    "sha256": hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:16],
                    "preview": _preview(value),
                }
            elif field in payload:
                info[field] = f"<{type(value).__name__}>"   # wrong type: say what it was
        if "content_id" in payload:
            info["content_id"] = payload.get("content_id")
    elif payload is not None:
        info["json_type"] = type(payload).__name__        # e.g. a bare list
    elif request.content_length:
        raw = request.get_data(cache=True)[:INPUT_PREVIEW_CHARS]
        info["raw_preview"] = raw.decode("utf-8", "replace")  # unparseable body
    return info


def _describe_output(response) -> dict:
    out = {"status": response.status_code}
    if response.is_json:
        body = response.get_json(silent=True)
        if isinstance(body, dict):
            for key in _OUTPUT_FIELDS:
                if key in body and key != "status":
                    out[key] = body[key]
            if "status" in body:
                out["item_status"] = body["status"]
    return out


def _outcome(status: int) -> str:
    if status >= 500:
        return "error"
    if status == 429:
        return "rate_limited"
    if status >= 400:
        return "rejected"
    return "ok"


def _settings() -> dict:
    """The settings that decide an outcome, so an old record explains itself."""
    return {
        "model": config.DETECTOR_MODEL,
        "human_threshold": config.HUMAN_THRESHOLD,
        "ai_threshold": config.AI_THRESHOLD,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
    }


def _record(status: int, response=None) -> dict:
    """Build the one structured record for this run (request)."""
    t0 = getattr(g, "t0", None)
    duration_ms = round((time.perf_counter() - t0) * 1000, 2) if t0 else None
    # CPU time used by the whole process during this request, summed over all
    # cores (torch runs gpt2 on several threads). Process-wide, so it is exact
    # only when requests don't overlap — measure_cost.py sends them one at a time.
    c0 = getattr(g, "cpu0", None)
    cpu_ms = round((time.process_time() - c0) * 1000, 2) if c0 is not None else None
    route = request.url_rule.rule if request.url_rule else request.path
    stages = getattr(g, "stages", {})

    entry = {
        "timestamp": _now(),
        "event": "request",
        "request_id": getattr(g, "request_id", None),
        "method": request.method,
        "route": route,
        "status": status,
        "outcome": _outcome(status),
        "duration_ms": duration_ms,
        "cpu_ms": cpu_ms,
        "input": _safe(_describe_input),
        "output": _describe_output(response) if response is not None else {"status": status},
        "stages_ms": stages,
        "settings": _settings(),
        "rss_mb": _note_rss(),
        "pid": os.getpid(),
    }
    entry.update(getattr(g, "ops_extra", {}))
    exc = getattr(g, "exception", None)
    if exc:
        entry["exception"] = exc

    with _lock:
        _status_counts[(request.method, route, status)] += 1
        if duration_ms is not None:
            _route_ms[route].append(duration_ms)
        for name, ms in stages.items():
            _stage_ms[name].append(ms)
    return entry


def _safe(fn):
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 — describing the input must not fail the log
        return {"unreadable": f"{type(exc).__name__}: {exc}"}


def _capture_exception(exc: BaseException):
    """Keep the exception's name, message and where it happened, for the record."""
    try:
        g.exception = {
            "type": type(exc).__name__,
            "message": str(exc)[:500],
            "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__)[-6:],
        }
    except RuntimeError:
        pass  # outside a request context


def init_app(app):
    """
    Hook every request: give it an id, time it, and write ONE structured
    record of it — including the requests that crash.

    after_request builds the record when there is a response. teardown_request
    always runs, so if after_request never did (an unhandled exception under
    `python app.py`, where debug mode lets it propagate), teardown writes an
    `outcome: "error"` record with the exception instead. A run that errored
    is never just a gap in the log.
    """
    from flask import got_request_exception

    @app.before_request
    def _start():
        g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        g.t0 = time.perf_counter()
        g.cpu0 = time.process_time()
        g.stages = {}
        g.ops_extra = {}

    def _on_exception(sender, exception, **_):
        _capture_exception(exception)

    got_request_exception.connect(_on_exception, app, weak=False)

    @app.after_request
    def _finish(response):
        if getattr(g, "t0", None) is None:  # never reached before_request
            return response

        entry = _record(response.status_code, response)
        g.ops_record = entry

        response.headers["X-Request-ID"] = g.request_id
        timing = [f"{name};dur={ms}" for name, ms in entry["stages_ms"].items()]
        timing.append(f"total;dur={entry['duration_ms']}")
        response.headers["Server-Timing"] = ", ".join(timing)
        return response

    @app.teardown_request
    def _write_record(exc):
        if getattr(g, "t0", None) is None:
            return
        entry = getattr(g, "ops_record", None)
        if entry is None:
            # No response was built: the request died. Record that it did.
            if exc is not None and getattr(g, "exception", None) is None:
                _capture_exception(exc)
            entry = _record(500)
            entry["outcome"] = "error"
        elif exc is not None and "exception" not in entry:
            _capture_exception(exc)
            entry["exception"] = g.exception
        if entry["route"] != "/metrics":  # polling the dashboard shouldn't flood the log
            _write(entry)


# ── Reading it back ──────────────────────────────────────────────────────────

def percentiles(values) -> dict:
    """count / p50 / p95 / p99 / max / mean for a list of milliseconds."""
    data = sorted(values)
    if not data:
        return {"count": 0}

    def pct(p):
        # nearest-rank: honest for small samples, no interpolation surprises
        k = max(0, min(len(data) - 1, math.ceil(p / 100 * len(data)) - 1))
        return round(data[k], 2)

    return {
        "count": len(data),
        "p50": pct(50),
        "p95": pct(95),
        "p99": pct(99),
        "max": round(data[-1], 2),
        "mean": round(sum(data) / len(data), 2),
    }


def snapshot() -> dict:
    """Everything /metrics returns."""
    import detector

    with _lock:
        statuses = [
            {"method": m, "route": r, "status": s, "count": n}
            for (m, r, s), n in sorted(_status_counts.items())
        ]
        routes = {r: percentiles(v) for r, v in _route_ms.items()}
        stages = {s: percentiles(v) for s, v in _stage_ms.items()}
        peak = _peak_rss_mb

    return {
        "pid": os.getpid(),
        "uptime_s": round(time.time() - _started_at, 1),
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": detector._model is not None,
        "model_load_s": _model_load_s,
        "rss_mb": rss_mb(),
        "peak_rss_mb": peak or None,
        "free_tier_budget_mb": FREE_TIER_MB,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "requests_by_status": statuses,
        "latency_ms_by_route": routes,
        "submit_stage_ms": stages,
        "window": f"last {_WINDOW} per route/stage, this process only",
    }


FREE_TIER_MB = 512


# ── File output ──────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _write(entry: dict):
    try:
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry, ensure_ascii=False, default=str)
        with _log_lock:
            with config.REQUEST_LOG.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
    except OSError:
        pass  # losing one ops line is better than failing the request


def read_requests(outcome: str | None = None, limit: int | None = None) -> list[dict]:
    """
    The run log, oldest first. Malformed lines are skipped.

        read_requests(outcome="error")      # every run that crashed
        read_requests(limit=20)             # the last 20 records
    """
    rows = _read_all()
    if outcome:
        rows = [r for r in rows if r.get("outcome") == outcome]
    return rows[-limit:] if limit else rows


def _read_all() -> list[dict]:
    if not config.REQUEST_LOG.exists():
        return []
    rows = []
    for line in config.REQUEST_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


# ── Reading it back from a terminal ──────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Read back logs/requests.jsonl.")
    ap.add_argument("--last", type=int, default=10, help="how many records (default 10)")
    ap.add_argument("--outcome", choices=["ok", "rejected", "rate_limited", "error"],
                    help="only records with this outcome")
    ap.add_argument("--json", action="store_true", help="print full records as JSON")
    args = ap.parse_args()

    records = read_requests(outcome=args.outcome, limit=args.last)
    if not records:
        print(f"No matching records in {config.REQUEST_LOG}")
    for r in records:
        if args.json:
            print(json.dumps(r, indent=2, ensure_ascii=False))
            continue
        dur = r.get("duration_ms", r.get("total_ms"))
        out = r.get("output") or {}
        detail = out.get("guess") or out.get("error") or ""
        if r.get("exception"):
            detail = f"{r['exception']['type']}: {r['exception']['message']}"
        print(f"{r.get('timestamp', '?'):<30} {r.get('outcome', '-'):<12} "
              f"{r.get('status', ''):<4} {r.get('method', r.get('event', '')):<7} "
              f"{r.get('route', ''):<9} {dur if dur is not None else '':>9} ms  {detail}")
