# Performance Baselines

This directory contains baseline performance measurements per platform.
Benchmarks are compared against these baselines to detect regressions.

## Files

- `linux-x64.json` -- Baseline from Linux CI runner
- `windows-x64.json` -- Baseline from Windows CI runner

## Creating / Updating Baselines

Run the benchmark with `--update-baseline` after confirming a known-good state:

```bash
python tests/perf/perf_bench.py \
    --core build/trident_libretro.so \
    --retroarch retroarch \
    --update-baseline
```

Baselines should only be updated after:
1. All tests pass
2. Performance numbers are verified as expected
3. The commit is known to be stable

## Notes

- CI baselines reflect CI runner hardware (shared VMs), not real-world performance
- Local baselines include hardware fingerprints for reproducibility
- Baselines are committed to the repo so CI can compare against them
