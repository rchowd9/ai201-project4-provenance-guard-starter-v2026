"""
Instrumentation — Shape A, "deploy and instrument".

The audit log (`audit.py`) answers *what did the service decide*. This module
answers *what did it cost to decide it*: how long each request took, where the
time went inside `/submit`, what status codes came back, and how much memory
the process is holding.

Three outputs, all from the same measurements:

    logs/requests.jsonl   one line per HTTP request — the operational log.
                          Append-only, like the audit log, and joined to it
                          by content_id. No submitted text is written here.
    GET /metrics          a live snapshot of the counters below, from memory.
    response headers      X-Request-ID and Server-Timing on every response,
                          so a single curl -i shows the stage breakdown.

The stages timed inside /submit match the five stages the README names, plus
the log write:

    validate → signal_one → signal_two → combine → label → audit_write

⚠️ The in-memory counters belong to one process. Under gunicorn with several
workers each worker has its own, so /metrics shows one worker's view. The
request log is shared by every worker, which is why `perf_report.py` builds its
numbers from the file rather than from /metrics.
"""

import json
import math
import os
import sys
import threading
import time
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
    detector.warm_up()
    _model_load_s = round(time.perf_counter() - start, 2)
    rss_after = _note_rss()

    event = {
        "timestamp": _now(),
        "event": "startup",
        "model": config.DETECTOR_MODEL,
        "model_load_s": _model_load_s,
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

def init_app(app):
    """Hook every request: give it an id, time it, log it, count it."""

    @app.before_request
    def _start():
        g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        g.t0 = time.perf_counter()
        g.stages = {}
        g.ops_extra = {}

    @app.after_request
    def _finish(response):
        t0 = getattr(g, "t0", None)
        if t0 is None:  # a request that never reached before_request
            return response

        total_ms = round((time.perf_counter() - t0) * 1000, 2)
        route = request.url_rule.rule if request.url_rule else request.path
        stages = getattr(g, "stages", {})
        current_rss = _note_rss()

        with _lock:
            _status_counts[(request.method, route, response.status_code)] += 1
            _route_ms[route].append(total_ms)
            for name, ms in stages.items():
                _stage_ms[name].append(ms)

        entry = {
            "timestamp": _now(),
            "request_id": g.request_id,
            "method": request.method,
            "route": route,
            "status": response.status_code,
            "total_ms": total_ms,
            "stages_ms": stages,
            "request_bytes": request.content_length,
            "rss_mb": current_rss,
            "pid": os.getpid(),
        }
        # Join key to the audit log, without re-logging the decision itself.
        if response.is_json and route in ("/submit", "/appeal"):
            body = response.get_json(silent=True)
            if isinstance(body, dict):
                for key in ("content_id", "guess", "error"):
                    if key in body:
                        entry[key] = body[key]
        entry.update(getattr(g, "ops_extra", {}))
        if route != "/metrics":  # polling the dashboard shouldn't flood the log
            _write(entry)

        response.headers["X-Request-ID"] = g.request_id
        timing = [f"{name};dur={ms}" for name, ms in stages.items()]
        timing.append(f"total;dur={total_ms}")
        response.headers["Server-Timing"] = ", ".join(timing)
        return response


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


def read_requests() -> list[dict]:
    """The ops log, oldest first. Malformed lines are skipped."""
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
