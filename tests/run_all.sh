#!/usr/bin/env bash
#
# Trident -- Local Test Orchestration
#
# Builds the core, test harness, and test ROMs, then runs both
# functional and performance tests. Works inside the Docker container
# or natively on Linux/macOS.
#
# Usage:
#   ./tests/run_all.sh                  # Run all tests
#   ./tests/run_all.sh functional       # Functional tests only
#   ./tests/run_all.sh perf             # Performance tests only
#   ./tests/run_all.sh --skip-build     # Skip build step
#
# Environment:
#   RETROARCH_PATH  - path to RetroArch binary (auto-detected if not set)
#   BUILD_DIR       - build directory (default: build)
#   JOBS            - parallel jobs (default: nproc/sysctl)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-$REPO_ROOT/build}"
RESULTS_DIR="$REPO_ROOT/test-results"

# Detect parallelism
if command -v nproc &>/dev/null; then
    JOBS="${JOBS:-$(nproc)}"
elif command -v sysctl &>/dev/null; then
    JOBS="${JOBS:-$(sysctl -n hw.logicalcpu)}"
else
    JOBS="${JOBS:-4}"
fi

# Parse args
RUN_FUNCTIONAL=true
RUN_PERF=true
SKIP_BUILD=false

for arg in "$@"; do
    case "$arg" in
        functional) RUN_PERF=false ;;
        perf)       RUN_FUNCTIONAL=false ;;
        --skip-build) SKIP_BUILD=true ;;
    esac
done

echo "╔══════════════════════════════════════╗"
echo "║   Trident Test Suite                 ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Repo:     $REPO_ROOT"
echo "Build:    $BUILD_DIR"
echo "Jobs:     $JOBS"
echo "Tests:    functional=$RUN_FUNCTIONAL perf=$RUN_PERF"
echo ""

mkdir -p "$RESULTS_DIR"

# ── Step 1: Build ──

if [ "$SKIP_BUILD" = false ]; then
    echo "=== Building core + test harness ==="

    CMAKE_ARGS="-DCMAKE_BUILD_TYPE=Release"
    CMAKE_ARGS="$CMAKE_ARGS -DBUILD_LIBRETRO_CORE=ON -DUSE_LIBRETRO_AUDIO=ON"
    CMAKE_ARGS="$CMAKE_ARGS -DENABLE_USER_BUILD=ON -DENABLE_VULKAN=OFF"
    CMAKE_ARGS="$CMAKE_ARGS -DENABLE_LUAJIT=OFF -DENABLE_DISCORD_RPC=OFF"
    CMAKE_ARGS="$CMAKE_ARGS -DENABLE_QT_GUI=OFF -DENABLE_OPENGL=ON"
    CMAKE_ARGS="$CMAKE_ARGS -DENABLE_HTTP_SERVER=OFF -DENABLE_TESTS=OFF"
    CMAKE_ARGS="$CMAKE_ARGS -DENABLE_METAL=OFF -DBUILD_TEST_HARNESS=ON"

    cmake -B "$BUILD_DIR" $CMAKE_ARGS "$REPO_ROOT"
    cmake --build "$BUILD_DIR" --config Release --target panda3ds_libretro -j"$JOBS"
    cmake --build "$BUILD_DIR" --config Release --target test_harness -j"$JOBS"
    echo ""
fi

# ── Detect core binary ──

CORE=""
for ext in so dylib dll; do
    candidate="$BUILD_DIR/trident_libretro.$ext"
    if [ -f "$candidate" ]; then
        CORE="$candidate"
        break
    fi
done

if [ -z "$CORE" ]; then
    echo "ERROR: Could not find trident_libretro in $BUILD_DIR"
    exit 1
fi
echo "Core: $CORE"

HARNESS="$BUILD_DIR/test_harness"
if [ ! -f "$HARNESS" ]; then
    echo "ERROR: Could not find test_harness in $BUILD_DIR"
    exit 1
fi
echo "Harness: $HARNESS"

EXIT_CODE=0

# ── Step 2: Functional tests ──

if [ "$RUN_FUNCTIONAL" = true ]; then
    echo ""
    echo "=== Functional Tests ==="
    python3 "$SCRIPT_DIR/functional/test_runner.py" \
        --harness "$HARNESS" \
        --core "$CORE" \
        --output "$RESULTS_DIR/functional.json" || EXIT_CODE=1
fi

# ── Step 3: Performance tests ──

if [ "$RUN_PERF" = true ]; then
    echo ""
    echo "=== Performance Tests ==="

    # Build test ROMs if needed
    ROM="$SCRIPT_DIR/perf/roms/simpler_tri.3dsx"
    if [ ! -f "$ROM" ]; then
        echo "Building test ROMs..."
        bash "$SCRIPT_DIR/perf/roms/build_roms.sh" || {
            echo "WARNING: Could not build test ROMs. Skipping perf tests."
            RUN_PERF=false
        }
    fi

    if [ "$RUN_PERF" = true ]; then
        # Detect RetroArch
        RA="${RETROARCH_PATH:-}"
        if [ -z "$RA" ]; then
            RA=$(command -v retroarch 2>/dev/null || true)
        fi

        if [ -z "$RA" ]; then
            echo "WARNING: RetroArch not found. Skipping perf tests."
            echo "  Set RETROARCH_PATH or install RetroArch."
        else
            PERF_CMD="python3 $SCRIPT_DIR/perf/perf_bench.py \
                --core $CORE --retroarch $RA \
                --local \
                --output $RESULTS_DIR/perf.json"

            if command -v xvfb-run &>/dev/null && [ -z "${DISPLAY:-}" ]; then
                xvfb-run $PERF_CMD || EXIT_CODE=1
            else
                $PERF_CMD || EXIT_CODE=1
            fi
        fi
    fi
fi

# ── Summary ──

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   Results                            ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Output directory: $RESULTS_DIR"
ls -la "$RESULTS_DIR"/ 2>/dev/null || true
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "All tests passed."
else
    echo "Some tests failed."
fi

exit $EXIT_CODE
