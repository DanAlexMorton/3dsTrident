# Trident -- Performance Evaluation

## Objective

Establish baseline performance metrics for the Trident 3DS libretro core across
platforms, identify bottlenecks, and track regressions over time.

---

## 1. Benchmark Suite

### Test Titles

Select titles that stress different subsystems. Each test runs for exactly
**2 minutes of gameplay** from a fixed save state or known starting point to
ensure reproducibility.

| Title | ID | Stress Target | Scene Description |
|-------|----|---------------|-------------------|
| Super Mario 3D Land | SM3DL | GPU (3D), CPU | World 1-1, run forward continuously |
| Mario Kart 7 | MK7 | GPU (3D), particles, audio | Mushroom Cup, Race 1, AI race |
| The Legend of Zelda: OoT 3D | OOT3D | GPU (shaders, lighting) | Hyrule Field, daytime, run around |
| Pokémon X/Y | PKXY | GPU (battles), CPU (overworld) | Battle scene (wild encounter) |
| New Super Mario Bros. 2 | NSMB2 | 2D rendering, audio | World 1-1, standard play |
| Shovel Knight | SK | 2D, audio-heavy | Stage 1, standard play |

### Metrics Collected

For each title on each platform, record:

| Metric | Unit | How to Measure |
|--------|------|----------------|
| **Average FPS** | frames/sec | RetroArch FPS counter (On-Screen Display) |
| **Minimum FPS** | frames/sec | Lowest observed during the 2-minute run |
| **Frame time (avg)** | ms | `1000 / avg_fps` |
| **Frame time (99th %)** | ms | RetroArch frame time widget or external tool |
| **CPU usage** | % | Task Manager (Win), `top` (Linux), Xcode Instruments (iOS) |
| **RAM usage (peak)** | MB | Same tools as CPU |
| **GPU usage** | % | GPU-Z (Win), `intel_gpu_top`/`nvidia-smi` (Linux), Xcode (iOS) |
| **Thermal throttle** | Y/N | Did sustained play cause FPS drop from thermal? (iOS/mobile) |
| **Audio glitches** | count | Audible pops, crackles, or dropouts during the run |
| **Shader compile stalls** | count | Visible hitches from shader compilation |

---

## 2. Platform Matrix

### Windows x64

| Config | Spec |
|--------|------|
| CPU | Document (e.g., i7-12700K, Ryzen 5 5600X) |
| GPU | Document (e.g., RTX 3060, integrated Intel UHD) |
| RAM | Document (e.g., 16 GB DDR4) |
| OS | Windows 10/11 |
| Renderer | OpenGL 4.1+ |
| RetroArch | Version |

### iOS ARM64

| Config | Spec |
|--------|------|
| Device | Document (e.g., iPhone 15 Pro) |
| Chip | Document (e.g., A17 Pro) |
| RAM | Document (e.g., 8 GB) |
| iOS | Version |
| Renderer | Metal |
| RetroArch | Version |

---

## 3. Results Template

### Per-Title Results

```
Platform: _______________
Title:    _______________
Date:     _______________
Core Version: ___________

Avg FPS:          _____ / 60
Min FPS:          _____
Avg Frame Time:   _____ ms
99th% Frame Time: _____ ms
CPU Usage:        _____ %
RAM (peak):       _____ MB
GPU Usage:        _____ %
Thermal Throttle: Y / N
Audio Glitches:   _____
Shader Stalls:    _____

Core Options:
  shader_jit:     enabled / disabled
  fastmem:        enabled / disabled
  ubershader:     enabled / disabled
  hash_textures:  enabled / disabled
  dsp_emulation:  HLE / LLE / Null
  accurate_mul:   enabled / disabled
  accelerate_shaders: enabled / disabled

Notes:
_________________________________
```

---

## 4. Core Options Impact Analysis

Test each option's performance impact using **one 3D title (SM3DL)** and
**one 2D title (NSMB2)**. Toggle one option at a time, keep all others at
defaults.

### Option: `trident_use_shader_jit`

| Setting | SM3DL Avg FPS | NSMB2 Avg FPS | Notes |
|---------|---------------|---------------|-------|
| enabled (default) | | | |
| disabled | | | |

### Option: `trident_use_fastmem`

| Setting | SM3DL Avg FPS | NSMB2 Avg FPS | Notes |
|---------|---------------|---------------|-------|
| enabled (default) | | | |
| disabled | | | |

### Option: `trident_use_ubershader`

| Setting | SM3DL Avg FPS | SM3DL Shader Stalls | Notes |
|---------|---------------|---------------------|-------|
| enabled (default) | | | |
| disabled | | | |

### Option: `trident_accelerate_shaders`

| Setting | SM3DL Avg FPS | NSMB2 Avg FPS | Notes |
|---------|---------------|---------------|-------|
| enabled (default) | | | |
| disabled | | | |

### Option: `trident_hash_textures`

| Setting | SM3DL Avg FPS | RAM (peak) | Notes |
|---------|---------------|------------|-------|
| enabled (default) | | | |
| disabled | | | |

### Option: `trident_accurate_shader_mul`

| Setting | SM3DL Avg FPS | Visual Difference? | Notes |
|---------|---------------|-------------------|-------|
| disabled (default) | | | |
| enabled | | | |

### Option: `trident_dsp_emulation`

| Setting | SM3DL Avg FPS | Audio Quality | Notes |
|---------|---------------|---------------|-------|
| HLE (default) | | | |
| LLE | | | |
| Null | | | |

---

## 5. Comparative Benchmarks

### Trident vs Citra (Windows)

Run the same test titles on the same machine with both cores.

| Title | Trident Avg FPS | Citra Avg FPS | Delta | Notes |
|-------|-----------------|---------------|-------|-------|
| SM3DL | | | | |
| MK7 | | | | |
| OOT3D | | | | |
| PKXY | | | | |
| NSMB2 | | | | |

### Cross-Platform (Trident)

| Title | Windows x64 | iOS (A17) | iOS (A15) | iOS (A11) | Notes |
|-------|-------------|-----------|-----------|-----------|-------|
| SM3DL | | | | | |
| NSMB2 | | | | | |
| OOT3D | | | | | |

---

## 6. Profiling Deep Dives

When a bottleneck is found, perform a targeted profiling session.

### CPU Profiling

- **Windows**: Use Visual Studio Performance Profiler or Very Sleepy
  - Attach to `retroarch.exe`, sample for 60 seconds during gameplay
  - Identify hot functions in `trident_libretro.dll`
- **iOS**: Use Xcode Instruments > Time Profiler
  - Focus on Metal command encoding and emulation loop

### GPU Profiling

- **Windows**: Use RenderDoc (if `ENABLE_RENDERDOC_API` is on) or GPU-Z
  - Capture a frame, inspect draw calls, shader complexity, overdraw
- **iOS**: Use Xcode Instruments > Metal System Trace
  - Check GPU encoder utilization, shader compilation time

### Memory Profiling

- **Windows**: Use Task Manager / Process Explorer, track Working Set over time
- **iOS**: Use Xcode Instruments > Allocations
  - Watch for unbounded growth (memory leak indicators)

---

## 7. Regression Testing

After each significant change, re-run the benchmark suite and compare.

### Tracking Table

| Date | Core Version | Commit | SM3DL FPS (Win) | SM3DL FPS (iOS) | Notes |
|------|-------------|--------|-----------------|-----------------|-------|
| | v1.0.0 | | | | Baseline |
| | | | | | |

### Automated Regression (Future)

Consider adding a CI step that:
1. Boots a known ROM in headless mode (if supported)
2. Runs for N frames
3. Records frame times
4. Compares against stored baselines
5. Fails if avg frame time regresses by >10%

---

## 8. Known Performance Considerations

### JIT Restrictions (iOS)

iOS does not allow JIT (just-in-time compilation) on non-jailbroken devices
without special entitlements. This affects:

- **CPU JIT (dynarmic)**: May fall back to interpreter, significant CPU perf hit
- **Shader JIT**: May be unavailable, shaders interpreted instead

Document whether Panda3DS's dynarmic backend works on iOS and the performance
impact of interpreter fallback.

### Metal vs OpenGL

The iOS build uses Metal while all other platforms use OpenGL. Performance
characteristics differ:

- Metal has lower driver overhead (fewer draw call bottlenecks)
- Metal shader compilation may behave differently (pipeline state caching)
- Validate that Metal renderer produces equivalent visual output

### Thermal Throttling (Mobile)

Sustained full-speed emulation will cause thermal throttling on mobile devices.
Document:

- Time to first throttle event
- Sustained FPS after throttling
- Recovery time when load decreases

---

## 9. Automated Performance Testing

An automated benchmark system is available in `tests/perf/`. It uses RetroArch's
CLI to run homebrew test ROMs through the Trident core and capture frame timing.

### Quick Start

```bash
# Build test ROMs (requires Docker or devkitARM)
./tests/perf/roms/build_roms.sh

# Run benchmarks locally
python tests/perf/perf_bench.py \
    --core build/trident_libretro.so \
    --retroarch retroarch \
    --local

# Save results as a new baseline
python tests/perf/perf_bench.py \
    --core build/trident_libretro.so \
    --retroarch retroarch \
    --update-baseline
```

### CI Integration

The GitHub Actions workflow `.github/workflows/perf.yml` runs benchmarks
automatically on every push to `main` and on pull requests. It:

1. Builds the core and test ROMs
2. Runs benchmarks on Linux and Windows CI runners
3. Compares against stored baselines in `tests/perf/baselines/`
4. Reports regressions (>15% avg FPS drop or >20% P99 frame time increase)
5. Posts a summary to the GitHub Actions step summary

Results are uploaded as workflow artifacts for each run.

### File Structure

```
tests/perf/
  perf_bench.py          # Benchmark runner script
  roms/                  # Test ROMs (compiled from vendor/Panda3DS/tests/)
    build_roms.sh        # Build script for test ROMs
  baselines/             # Known-good performance baselines per platform
  results/               # Local results (gitignored)
```

### Output Format

Results are stored as JSON with per-ROM metrics:
- `avg_fps` -- Average frames per second
- `min_fps` -- Minimum observed FPS
- `p99_frame_time_ms` -- 99th percentile frame time
- `std_dev_ms` -- Standard deviation of frame times

---

## Sign-Off

| Evaluator | Date | Platforms Tested | Summary |
|-----------|------|------------------|---------|
| | | | |
