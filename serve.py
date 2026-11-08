#!/usr/bin/env python3
"""
Run Provenance Guard the deployed way — Shape A, Path B (local, with logs).

    python serve.py                 # http://127.0.0.1:5000, debug off, model warm
    HOST=0.0.0.0 PORT=8080 python serve.py

How it differs from `python app.py`:

  * Debug is off. No interactive debugger, no reloader double-loading gpt2.
  * The model loads BEFORE the port opens, and the load is timed and logged
    (`event: startup` in logs/requests.jsonl). Nobody's first request pays 10–20 s.
  * It prints the memory the process holds once the model is in, against the
    512 MB a free host gives you. That's the arithmetic behind Path B.
  * A real WSGI server where one exists: gunicorn on Linux/macOS. gunicorn
    doesn't run on Windows (it needs fcntl), so there it uses waitress if
    installed, otherwise Flask's threaded server with debug off.

On Linux/macOS you can also run gunicorn directly:

    AI201_WARMUP=1 gunicorn app:app --bind 0.0.0.0:$PORT --preload --workers 1

Keep it at ONE worker. Each worker holds its own copy of gpt2 (~500 MB+), and
the rate limiter's memory:// store isn't shared between workers, so two
workers would also double everyone's limit.
"""

import os
import sys

# Must be set before app is imported: app.py warms the model at import time
# when this is on, which is also what makes `gunicorn --preload` warm once.
os.environ.setdefault("AI201_WARMUP", "1")
os.environ.setdefault("AI201_DEBUG", "0")

import config  # noqa: E402


def _banner(startup: dict | None):
    import instrumentation

    rss = instrumentation.rss_mb()
    budget = instrumentation.FREE_TIER_MB
    print(f"Provenance Guard (served) on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:   {config.DETECTOR_MODEL}")
    if startup:
        print(f"  model load:       {startup['model_load_s']} s (before the port opened)")
        if startup.get("first_pass_s") is not None:
            print(f"  first gpt2 pass:  {startup['first_pass_s']} s (torch setup, paid at startup)")
    print(f"  resident memory:  {rss} MB  (free-tier budget {budget} MB"
          + (f", {'OVER' if rss > budget else 'under'} by {abs(rss - budget):.0f} MB)" if rss else ")"))
    print(f"  rate limiting:    {'ON' if config.RATE_LIMITING_ENABLED else 'off'}"
          f"  ({config.RATE_LIMIT_PER_MINUTE}/min, {config.RATE_LIMIT_PER_DAY}/day)")
    print(f"  audit log:        {config.AUDIT_LOG}")
    print(f"  request log:      {config.REQUEST_LOG}")
    print(f"  live metrics:     http://{config.HOST}:{config.PORT}/metrics")
    print()


def main():
    print(f"Loading {config.DETECTOR_MODEL} before opening the port…", flush=True)
    import app as service  # warms the model (AI201_WARMUP=1)
    import instrumentation

    startup = None
    for row in reversed(instrumentation.read_requests()):
        if row.get("event") == "startup" and row.get("pid") == os.getpid():
            startup = row
            break
    _banner(startup)

    if sys.platform != "win32":
        try:
            from gunicorn.app.base import BaseApplication

            class _Gunicorn(BaseApplication):
                def load_config(self):
                    self.cfg.set("bind", f"{config.HOST}:{config.PORT}")
                    self.cfg.set("workers", 1)
                    self.cfg.set("threads", 4)
                    self.cfg.set("timeout", 120)  # a 400-token gpt2 pass on a slow CPU

                def load(self):
                    return service.app

            print("server: gunicorn (1 worker, 4 threads)", flush=True)
            _Gunicorn().run()
            return
        except ImportError:
            pass

    try:
        from waitress import serve

        print("server: waitress (8 threads)", flush=True)
        serve(service.app, host=config.HOST, port=config.PORT, threads=8)
    except ImportError:
        print("server: Flask threaded, debug off "
              "(gunicorn doesn't run on Windows; `pip install waitress` for a real one)",
              flush=True)
        service.app.run(host=config.HOST, port=config.PORT, debug=False,
                        threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
