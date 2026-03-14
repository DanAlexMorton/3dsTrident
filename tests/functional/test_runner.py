#!/usr/bin/env python3
"""
Trident Functional Test Runner

Orchestrates the C test harness, parses its output, and produces
structured JSON results.

Usage:
    python test_runner.py --harness <path> --core <path> [--rom <path>]
"""

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR.parent / "perf" / "results"


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


def get_git_commit():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def run_harness(harness_path, core_path, rom_path=None, timeout=120):
    """Run the test harness and capture output."""
    cmd = [str(harness_path), str(core_path)]
    if rom_path:
        cmd.append(str(rom_path))

    start = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, "Harness timed out"
    except FileNotFoundError:
        return None, f"Harness not found: {harness_path}"

    elapsed = time.monotonic() - start
    output = result.stdout + result.stderr
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "elapsed_s": round(elapsed, 2),
    }, None


def parse_results(stdout):
    """Parse PASS/FAIL/SKIP lines from harness output."""
    tests = []
    pattern = re.compile(r"^(PASS|FAIL|SKIP):\s+(\S+)(?:\s+--\s+(.*))?$")

    for line in stdout.split("\n"):
        m = pattern.match(line.strip())
        if m:
            status = m.group(1).lower()
            name = m.group(2)
            detail = m.group(3) or ""
            tests.append({
                "name": name,
                "status": "passed" if status == "pass" else ("failed" if status == "fail" else "skipped"),
                "detail": detail,
            })

    summary_passed = 0
    summary_failed = 0
    summary_skipped = 0
    for line in stdout.split("\n"):
        m = re.match(r"PASSED:\s+(\d+)", line)
        if m:
            summary_passed = int(m.group(1))
        m = re.match(r"FAILED:\s+(\d+)", line)
        if m:
            summary_failed = int(m.group(1))
        m = re.match(r"SKIPPED:\s+(\d+)", line)
        if m:
            summary_skipped = int(m.group(1))

    return tests, summary_passed, summary_failed, summary_skipped


def format_table(tests):
    """Format test results as a readable table."""
    lines = []
    lines.append(f"{'Test':<30} {'Status':<8} {'Detail'}")
    lines.append("-" * 70)
    for t in tests:
        status = t["status"].upper()
        lines.append(f"{t['name']:<30} {status:<8} {t['detail']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Trident Functional Test Runner")
    parser.add_argument("--harness", required=True, help="Path to test_harness executable")
    parser.add_argument("--core", required=True, help="Path to trident_libretro core binary")
    parser.add_argument("--rom", help="Path to test ROM for Level 2 tests")
    parser.add_argument("--output", help="Output JSON path")
    parser.add_argument("--platform", help="Override platform name")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout in seconds")
    args = parser.parse_args()

    harness_path = Path(args.harness).resolve()
    core_path = Path(args.core).resolve()
    rom_path = Path(args.rom).resolve() if args.rom else None
    plat = args.platform or detect_platform()

    if not harness_path.exists():
        print(f"ERROR: Harness not found: {harness_path}")
        sys.exit(1)
    if not core_path.exists():
        print(f"ERROR: Core not found: {core_path}")
        sys.exit(1)

    print(f"=== Trident Functional Tests ===")
    print(f"Platform:  {plat}")
    print(f"Harness:   {harness_path}")
    print(f"Core:      {core_path}")
    if rom_path:
        print(f"ROM:       {rom_path}")
    print()

    raw, err = run_harness(harness_path, core_path, rom_path, args.timeout)
    if err:
        print(f"ERROR: {err}")
        sys.exit(1)

    print(raw["stdout"])
    if raw["stderr"]:
        print("--- stderr ---")
        print(raw["stderr"])

    tests, passed, failed, skipped = parse_results(raw["stdout"])

    print()
    print(format_table(tests))
    print()
    print(f"Passed: {passed}  Failed: {failed}  Skipped: {skipped}")
    print(f"Elapsed: {raw['elapsed_s']}s")

    results = {
        "type": "functional",
        "platform": plat,
        "commit": get_git_commit(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exit_code": raw["exit_code"],
        "elapsed_s": raw["elapsed_s"],
        "summary": {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": passed + failed + skipped,
        },
        "tests": tests,
    }

    if args.output:
        output_path = Path(args.output)
    else:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = RESULTS_DIR / f"functional_{plat}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
