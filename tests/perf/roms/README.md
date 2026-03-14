# Performance Test ROMs

This directory contains pre-built `.3dsx` homebrew ROMs used for automated
performance benchmarking. These are compiled from the test sources in
`vendor/Panda3DS/tests/`.

## Building

If the `.3dsx` files are not present, build them using the devkitPro Docker image:

```bash
./build_roms.sh
```

Requires Docker. The script uses `devkitpro/devkitarm` to cross-compile.

The CI workflow (`perf.yml`) builds these automatically.

## ROM Sources and Licenses

| ROM | Source | License |
|-----|--------|---------|
| `simpler_tri.3dsx` | `vendor/Panda3DS/tests/SimplerTri/` | Same as Panda3DS (GPL-3.0) |

## What They Test

- **simpler_tri.3dsx**: Renders a single orange triangle in an infinite loop
  using Citro3D. Minimal GPU load, stable frame timing -- ideal for detecting
  CPU-side regressions.
