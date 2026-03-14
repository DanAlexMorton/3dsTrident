# Trident - 3DS Libretro Core

[![Build](https://github.com/DanAlexMorton/3dsEmulator/actions/workflows/build.yml/badge.svg)](https://github.com/DanAlexMorton/3dsEmulator/actions/workflows/build.yml)

A 3DS libretro core powered by [Panda3DS](https://github.com/wheremyfoodat/Panda3DS), designed for use with RetroArch and architected for RetroAchievements support.

## Downloads

Pre-built binaries for Windows, Linux, and macOS are available on the [Releases](https://github.com/DanAlexMorton/3dsEmulator/releases) page.

## Building from Source

### Prerequisites (all platforms)
- CMake 3.16+
- Git
- A C++20 compiler

### Windows

```bash
git clone --recursive https://github.com/DanAlexMorton/3dsEmulator.git
cd 3dsEmulator
cmake -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release --target panda3ds_libretro
```

Output: `build/Release/trident_libretro.dll`

### Linux

```bash
git clone --recursive https://github.com/DanAlexMorton/3dsEmulator.git
cd 3dsEmulator
sudo apt-get install build-essential cmake libgl-dev libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target panda3ds_libretro -j$(nproc)
```

Output: `build/trident_libretro.so`

### macOS

```bash
git clone --recursive https://github.com/DanAlexMorton/3dsEmulator.git
cd 3dsEmulator
cmake -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_OSX_ARCHITECTURES="x86_64;arm64" -DENABLE_METAL=OFF
cmake --build build --target panda3ds_libretro -j$(sysctl -n hw.logicalcpu)
```

Output: `build/trident_libretro.dylib`

## Installation

1. Copy `trident_libretro.dll` / `.so` / `.dylib` to your RetroArch `cores/` directory
2. Copy `trident_libretro.info` to RetroArch's `info/` directory
3. Launch RetroArch, load the core, and load a 3DS ROM

## Supported Formats

`.3ds`, `.3dsx`, `.elf`, `.axf`, `.cci`, `.cxi`, `.app`, `.ncch`

## Platform Support

| Platform | Status |
|----------|--------|
| Windows x64 | Supported |
| Linux x64 | Supported |
| macOS x64 / ARM64 | Supported |
| Android ARM64 | Experimental |

Requires OpenGL 4.1+ (or OpenGL ES 3.2 on mobile).

## License

GPL-3.0 -- see [LICENSE](LICENSE) for details.
