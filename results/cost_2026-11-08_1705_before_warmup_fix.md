# Cost of one run — 2026-11-08 17:05

**The cost unit is compute, not money.** Provenance Guard calls no paid API, so a run has no API spend and no billed tokens. What a run consumes is CPU time for one local gpt2 pass, so it's measured in CPU-seconds and wall-clock seconds, with gpt2 tokens read as the unit of work.

## Result — average of 10 runs

| Measure | Mean | SD | Min | Max |
|---|---|---|---|---|
| **CPU time per run** (all cores) | **4,209.4 ms** | 689.4 | 3,609.4 | 6,046.9 |
| **Wall time per run** (server) | **1,525.0 ms** | 1,593.6 | 899.7 | 6,056.9 |
| of which signal one (gpt2) | 1,519.3 ms | 1,592.8 | 893.9 | 6,048.9 |
| Wall time seen by client | 1,535.6 ms | 1,600.1 | 905.5 | 6,085.7 |
| Cores busy (CPU ÷ wall) | 3.64 | 0.99 | 1.00 | 4.55 |
| gpt2 tokens read | 269 | 0 | 269 | 269 |
| CPU per token | 15.65 ms | 2.56 | 13.42 | 22.48 |
| Server memory (RSS) | 1,050 MB | | 974 | 1,136 |

Baseline, `GET /health` ×10 (no model): CPU 46.88 ms, wall 50.66 ms. That is the cost of the framework alone; a run costs 90× it.

**What that comes to, from the measured mean (arithmetic, not a price list):**

- 1,000 runs ≈ **70.2 CPU-minutes**, 25.4 minutes of wall time one at a time.
- One core-hour of CPU covers ≈ **855 runs**.
- One client sending back-to-back gets ≈ 0.7 runs/s.

## Every run

| Run | Status | request_id | Client ms | Server wall ms | CPU ms | signal_one ms | Cores | Tokens | Guess |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 200 | `cost-fe166ad9` | 6,085.7 | 6,056.9 | 6,046.9 | 6,048.9 | 1.00 | 269 | unsure |
| 2 | 200 | `cost-23885385` | 1,138.1 | 1,109.4 | 4,156.2 | 1,103.7 | 3.75 | 269 | unsure |
| 3 | 200 | `cost-ce769fcb` | 1,089.9 | 1,083.8 | 3,609.4 | 1,077.8 | 3.33 | 269 | unsure |
| 4 | 200 | `cost-56b3b5a6` | 1,008.2 | 1,001.6 | 3,671.9 | 995.9 | 3.67 | 269 | unsure |
| 5 | 200 | `cost-ab447dad` | 1,011.1 | 1,005.9 | 4,312.5 | 1,000.8 | 4.29 | 269 | unsure |
| 6 | 200 | `cost-f8edb7d9` | 905.5 | 899.7 | 4,093.8 | 893.9 | 4.55 | 269 | unsure |
| 7 | 200 | `cost-796e317d` | 1,014.8 | 1,008.3 | 3,953.1 | 1,002.6 | 3.92 | 269 | unsure |
| 8 | 200 | `cost-5dcfdc95` | 1,066.1 | 1,059.8 | 4,125.0 | 1,054.1 | 3.89 | 269 | unsure |
| 9 | 200 | `cost-af1b7c7c` | 1,076.4 | 1,070.4 | 4,296.9 | 1,065.4 | 4.01 | 269 | unsure |
| 10 | 200 | `cost-2c185529` | 960.5 | 954.6 | 3,828.1 | 949.6 | 4.01 | 269 | unsure |

## How this was measured

- **The run:** one `POST /submit` with the same fixed ~230-word text (1250 chars), sent 10 times, strictly one after another, each under its own creator_id so the rate limit can't interfere.
- **CPU time:** the service records `time.process_time()` at the start and end of every request (`instrumentation.py`, before/after hooks) and logs the difference as `cpu_ms`. That's CPU time for the whole server process, summed over every core torch used, so it can exceed wall time. Because it's process-wide, the runs never overlap.
- **Wall time:** `time.perf_counter()` across the same request, logged as `duration_ms`. Signal one's share is the `signal_one` stage timer.
- **Tokens:** the gpt2 tokenizer's count for the text, capped at 400, logged as `model_tokens`.
- **Source:** every number above was read back from that request's record in `logs/requests.jsonl` by its `X-Request-ID`, not computed by this script. Client time is the only figure taken here.
- **Model state:** the service was started with `serve.py`, so gpt2 was already in memory and no run includes the model load (`detector_loaded` was True before run 1).

**Machine:** Windows 11, AMD64 Family 23 Model 160 Stepping 0, AuthenticAMD, 8 logical CPUs, torch default 4 threads, Python 3.13.15, model `gpt2`, CPU only. These numbers belong to this machine; a different CPU gives different ones, which is why it's measured and not looked up.
