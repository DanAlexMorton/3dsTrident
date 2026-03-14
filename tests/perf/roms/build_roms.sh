#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TESTS_DIR="$REPO_ROOT/vendor/Panda3DS/tests"

build_rom() {
    local test_name="$1"
    local output_name="$2"
    local test_dir="$TESTS_DIR/$test_name"

    if [ ! -d "$test_dir" ]; then
        echo "ERROR: Test directory not found: $test_dir"
        return 1
    fi

    echo "Building $test_name -> $output_name.3dsx"

    if command -v make &>/dev/null && [ -n "${DEVKITARM:-}" ]; then
        # Native devkitARM build
        make -C "$test_dir" clean 2>/dev/null || true
        make -C "$test_dir"
        cp "$test_dir/$test_name.3dsx" "$SCRIPT_DIR/$output_name.3dsx"
    elif command -v docker &>/dev/null; then
        # Docker-based build
        docker run --rm \
            -v "$REPO_ROOT:/build" \
            -w "/build/vendor/Panda3DS/tests/$test_name" \
            devkitpro/devkitarm:latest \
            bash -c "make clean 2>/dev/null; make"
        cp "$test_dir/$test_name.3dsx" "$SCRIPT_DIR/$output_name.3dsx"
    else
        echo "ERROR: Neither devkitARM nor Docker available. Cannot build test ROMs."
        echo "Install Docker and run this script again, or install devkitPro."
        return 1
    fi

    echo "Built: $SCRIPT_DIR/$output_name.3dsx"
}

echo "=== Building performance test ROMs ==="
build_rom "SimplerTri" "simpler_tri"
echo "=== Done ==="
