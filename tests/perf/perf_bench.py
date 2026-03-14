#!/usr/bin/env python3
"""
Trident Performance Benchmark Runner

Runs homebrew 3DS ROMs through RetroArch with the Trident core,
captures frame timing data, and compares against baselines to
detect regressions.

Usage:
    python perf_bench.py --core <path> --retroarch <path> [options]

Examples:
    # CI mode (auto-detect platform, compare vs baseline)
    python perf_bench.py --core build/trident_libretro.so --retroarch /usr/bin/retroarch

    # Local mode with hardware info
    python perf_bench.py --core build/trident_libretro.so --retroarch retroarch --local

    # Update baseline after a known-good run
    python perf_bench.py --core build/trident_libretro.so --retroarch retroarch --update-baseline
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROMS_DIR = SCRIPT_DIR / "roms"
BASELINES_DIR = SCRIPT_DIR / "baselines"
RESULTS_DIR = SCRIPT_DIR / "results"

DEFAULT_FRAMES = 600  # 10 seconds at 60fps
REGRESSION_FPS_THRESHOLD = 0.15  # 15% avg FPS drop
REGRESSION_P99_THRESHOLD = 0.20  # 20% 99th percentile increase


def detect_platform():
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        return "windows-x64"
    elif system == "linux":
        if "aarch64" in machine or "arm64" in machine:
            return "linux-arm64"
        return "linux-x64"
    elif system == "darwin":
        if "arm64" in machine:
            return "macos-arm64"
        return "macos-x64"
    return f"{system}-{machine}"


def get_hardware_info():
    info = {
        "os": f"{platform.system()} {platform.release()}",
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": platform.python_version(),
    }
    try:
        import psutil
        info["cpu_count"] = psutil.cpu_count(logical=True)
        info["ram_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)
    except ImportError:
        info["cpu_count"] = os.cpu_count()
    return info


def find_roms():
    roms = sorted(ROMS_DIR.glob("*.3dsx"))
    if not roms:
        print(f"WARNING: No .3dsx ROMs found in {ROMS_DIR}")
        print("Run tests/perf/roms/build_roms.sh to compile test ROMs.")
    return roms


def run_benchmark(retroarch_path, core_path, rom_path, num_frames, timeout=300):
    """Run RetroArch with the core and ROM, capture frame timing output."""

    cmd = [
        str(retroarch_path),
        "-L", str(core_path),
        str(rom_path),
        "--max-frames", str(num_frames),
        "--verbose",
    ]

    env = os.environ.copy()
    # Use software video driver on headless CI
    if os.environ.get("CI"):
        env["DISPLAY"] = os.environ.get("DISPLAY", ":99")

    print(f"  Running: {rom_path.name} for {num_frames} frames...")
    start_time = time.monotonic()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after {timeout}s")
        return None
    except FileNotFoundError:
        print(f"  ERROR: RetroArch not found at {retroarch_path}")
        return None

    elapsed = time.monotonic() - start_time
    output = result.stdout + result.stderr

    return parse_frame_times(output, elapsed, num_frames)


def parse_frame_times(output, wall_time, expected_frames):
    """Parse RetroArch verbose output for frame timing data."""

    frame_times = []

    # RetroArch logs frame time in various formats depending on version
    # Pattern 1: "[Video]: Frame time: 16.67 ms"
    # Pattern 2: "Frametime: 16.67ms"
    # Pattern 3: timing info in --verbose output
    patterns = [
        re.compile(r"[Ff]rame\s*time[:\s]+(\d+\.?\d*)\s*ms", re.IGNORECASE),
        re.compile(r"[Ff]rametime[:\s]+(\d+\.?\d*)\s*ms", re.IGNORECASE),
    ]

    for line in output.split("\n"):
        for pattern in patterns:
            match = pattern.search(line)
            if match:
                frame_times.append(float(match.group(1)))
                break

    if not frame_times:
        # Fallback: estimate from wall time if no per-frame data available
        if wall_time > 0 and expected_frames > 0:
            avg_frame_time = (wall_time * 1000) / expected_frames
            return {
                "source": "wall_clock",
                "frames_measured": expected_frames,
                "wall_time_s": round(wall_time, 2),
                "avg_fps": round(expected_frames / wall_time, 2),
                "min_fps": None,
                "avg_frame_time_ms": round(avg_frame_time, 2),
                "p99_frame_time_ms": None,
                "std_dev_ms": None,
            }
        return None

    avg_ft = statistics.mean(frame_times)
    fps_values = [1000.0 / ft if ft > 0 else 0 for ft in frame_times]

    result = {
        "source": "frame_times",
        "frames_measured": len(frame_times),
        "wall_time_s": round(wall_time, 2),
        "avg_fps": round(statistics.mean(fps_values), 2),
        "min_fps": round(min(fps_values), 2) if fps_values else None,
        "avg_frame_time_ms": round(avg_ft, 2),
        "p99_frame_time_ms": round(sorted(frame_times)[int(len(frame_times) * 0.99)], 2),
        "std_dev_ms": round(statistics.stdev(frame_times), 2) if len(frame_times) > 1 else 0,
    }
    return result


def compare_with_baseline(current, baseline):
    """Compare current results against baseline, return list of regressions."""
    regressions = []

    baseline_by_rom = {b["rom"]: b for b in baseline.get("benchmarks", [])}

    for bench in current.get("benchmarks", []):
        rom = bench["rom"]
        base = baseline_by_rom.get(rom)
        if not base:
            continue

        cur_fps = bench.get("avg_fps")
        base_fps = base.get("avg_fps")

        if cur_fps and base_fps and base_fps > 0:
            fps_delta = (base_fps - cur_fps) / base_fps
            if fps_delta > REGRESSION_FPS_THRESHOLD:
                regressions.append({
                    "rom": rom,
                    "metric": "avg_fps",
                    "baseline": base_fps,
                    "current": cur_fps,
                    "delta_pct": round(fps_delta * 100, 1),
                    "threshold_pct": REGRESSION_FPS_THRESHOLD * 100,
                })

        cur_p99 = bench.get("p99_frame_time_ms")
        base_p99 = base.get("p99_frame_time_ms")

        if cur_p99 and base_p99 and base_p99 > 0:
            p99_delta = (cur_p99 - base_p99) / base_p99
            if p99_delta > REGRESSION_P99_THRESHOLD:
                regressions.append({
                    "rom": rom,
                    "metric": "p99_frame_time_ms",
                    "baseline": base_p99,
                    "current": cur_p99,
                    "delta_pct": round(p99_delta * 100, 1),
                    "threshold_pct": REGRESSION_P99_THRESHOLD * 100,
                })

    return regressions


def format_results_table(results):
    """Format benchmark results as a readable table."""
    lines = []
    lines.append(f"Platform: {results['platform']}")
    lines.append(f"Commit:   {results.get('commit', 'unknown')}")
    lines.append(f"Time:     {results['timestamp']}")
    lines.append("")
    lines.append(f"{'ROM':<25} {'Avg FPS':>8} {'Min FPS':>8} {'P99 FT':>8} {'StdDev':>8} {'Source':>12}")
    lines.append("-" * 75)

    for b in results["benchmarks"]:
        avg = f"{b['avg_fps']:.1f}" if b.get("avg_fps") else "N/A"
        mn = f"{b['min_fps']:.1f}" if b.get("min_fps") else "N/A"
        p99 = f"{b['p99_frame_time_ms']:.1f}ms" if b.get("p99_frame_time_ms") else "N/A"
        sd = f"{b['std_dev_ms']:.1f}ms" if b.get("std_dev_ms") else "N/A"
        src = b.get("source", "unknown")
        lines.append(f"{b['rom']:<25} {avg:>8} {mn:>8} {p99:>8} {sd:>8} {src:>12}")

    return "\n".join(lines)


def format_regression_report(regressions):
    """Format regression warnings."""
    if not regressions:
        return "No regressions detected."

    lines = ["PERFORMANCE REGRESSIONS DETECTED:", ""]
    for r in regressions:
        lines.append(
            f"  [{r['rom']}] {r['metric']}: "
            f"{r['baseline']} -> {r['current']} "
            f"({r['delta_pct']}% change, threshold: {r['threshold_pct']}%)"
        )
    return "\n".join(lines)


def get_git_commit():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(description="Trident Performance Benchmark Runner")
    parser.add_argument("--core", required=True, help="Path to trident_libretro core binary")
    parser.add_argument("--retroarch", required=True, help="Path to RetroArch executable")
    parser.add_argument("--frames", type=int, default=DEFAULT_FRAMES, help=f"Frames to run per ROM (default: {DEFAULT_FRAMES})")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout per ROM in seconds (default: 300)")
    parser.add_argument("--local", action="store_true", help="Local mode: include hardware info")
    parser.add_argument("--update-baseline", action="store_true", help="Save results as new baseline")
    parser.add_argument("--output", help="Output JSON path (default: auto-generated)")
    parser.add_argument("--platform", help="Override platform name (default: auto-detect)")
    args = parser.parse_args()

    core_path = Path(args.core).resolve()
    retroarch_path = shutil.which(args.retroarch) or Path(args.retroarch).resolve()

    if not core_path.exists():
        print(f"ERROR: Core not found: {core_path}")
        sys.exit(1)

    plat = args.platform or detect_platform()
    roms = find_roms()
    if not roms:
        print("ERROR: No test ROMs available. Run tests/perf/roms/build_roms.sh first.")
        sys.exit(1)

    print(f"=== Trident Performance Benchmark ===")
    print(f"Platform:  {plat}")
    print(f"Core:      {core_path}")
    print(f"RetroArch: {retroarch_path}")
    print(f"ROMs:      {len(roms)}")
    print(f"Frames:    {args.frames}")
    print()

    results = {
        "platform": plat,
        "commit": get_git_commit(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "frames_requested": args.frames,
        "benchmarks": [],
    }

    if args.local:
        results["hardware"] = get_hardware_info()

    for rom in roms:
        timing = run_benchmark(retroarch_path, core_path, rom, args.frames, args.timeout)
        bench = {"rom": rom.name}
        if timing:
            bench.update(timing)
            print(f"  -> Avg FPS: {timing.get('avg_fps', 'N/A')}, "
                  f"P99: {timing.get('p99_frame_time_ms', 'N/A')}ms "
                  f"({timing.get('source', '?')})")
        else:
            bench["error"] = "Benchmark failed or timed out"
            print(f"  -> FAILED")
        results["benchmarks"].append(bench)

    print()
    print(format_results_table(results))
    print()

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = RESULTS_DIR / f"{plat}_{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_path}")

    # Compare with baseline
    baseline_path = BASELINES_DIR / f"{plat}.json"
    if baseline_path.exists():
        with open(baseline_path) as f:
            baseline = json.load(f)
        regressions = compare_with_baseline(results, baseline)
        report = format_regression_report(regressions)
        print()
        print(report)

        if regressions:
            # Write regression report for CI consumption
            report_path = RESULTS_DIR / f"{plat}_regressions.txt"
            with open(report_path, "w") as f:
                f.write(report)
            sys.exit(1)
    else:
        print(f"\nNo baseline found at {baseline_path}. Run with --update-baseline to create one.")

    # Update baseline if requested
    if args.update_baseline:
        BASELINES_DIR.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Baseline updated: {baseline_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
