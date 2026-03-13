# 3DS Emulator - Libretro Core

A 3DS libretro core built on [Panda3DS](https://github.com/wheremyfoodat/Panda3DS), designed for use with RetroArch and architected for RetroAchievements support.

## Building (Windows)

Prerequisites:
- Visual Studio 2022 with C++ Desktop workload
- CMake 3.16+
- Git

```bash
git clone --recursive https://github.com/DanAlexMorton/3dsEmulator.git
cd 3dsEmulator
cmake -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release --target panda3ds_libretro
```

Output: `build/Release/panda3ds_libretro.dll`

## Installation

1. Copy `panda3ds_libretro.dll` to your RetroArch `cores/` directory
2. Copy `vendor/Panda3DS/docs/libretro/panda3ds_libretro.info` to RetroArch's `info/` directory
3. Launch RetroArch, load the core, and load a 3DS ROM

## Supported Formats

`.3ds`, `.3dsx`, `.elf`, `.axf`, `.cci`, `.cxi`, `.app`, `.ncch`

## License

Apache License 2.0
