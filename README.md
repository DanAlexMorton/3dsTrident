# Trident - 3DS Libretro Core

[![Build](https://github.com/DanAlexMorton/3dsTrident/actions/workflows/build.yml/badge.svg)](https://github.com/DanAlexMorton/3dsTrident/actions/workflows/build.yml)

A 3DS libretro core powered by [Panda3DS](https://github.com/wheremyfoodat/Panda3DS), designed for use with RetroArch and architected for RetroAchievements support.

## Downloads

Pre-built binaries for all platforms are available on the [Releases](https://github.com/DanAlexMorton/3dsTrident/releases) page.

## Platform Support

| Platform | Status | Renderer | Binary |
|----------|--------|----------|--------|
| Windows x64 | Supported | OpenGL 4.1+ | `trident_libretro.dll` |
| Linux x64 | Supported | OpenGL 4.1+ | `trident_libretro.so` |
| macOS ARM64 | Supported | OpenGL 4.1+ | `trident_libretro.dylib` |
| macOS x64 | Supported | OpenGL 4.1+ | `trident_libretro.dylib` |
| Android ARM64 | Experimental | OpenGL ES 3.2 | `trident_libretro.so` |
| iOS ARM64 | Experimental | Metal | `trident_libretro.dylib` |

## Installation

### Windows / Linux / macOS

1. Download the binary for your platform from [Releases](https://github.com/DanAlexMorton/3dsTrident/releases)
2. Copy the core file to your RetroArch `cores/` directory
3. Copy `trident_libretro.info` to RetroArch's `info/` directory
4. Launch RetroArch > Load Core > Trident > Load a 3DS ROM

### Android

1. Download `trident_libretro_android_arm64.so` from [Releases](https://github.com/DanAlexMorton/3dsTrident/releases)
2. Rename it to `trident_libretro_android.so`
3. Copy it to RetroArch's cores directory, typically:
   - **Internal storage**: `/storage/emulated/0/RetroArch/cores/`
   - **Or via RetroArch**: Settings > Directory > Cores — note the path and place the file there
4. Copy `trident_libretro.info` to RetroArch's `info/` directory (same parent as `cores/`)
5. Launch RetroArch > Load Core > Trident > Load a 3DS ROM
6. A device with a Snapdragon 845 / Exynos 9810 or newer is recommended

### iOS

1. Install RetroArch on your iOS device via [AltStore](https://altstore.io/), [TrollStore](https://github.com/opa334/TrollStore), or a developer account
2. Download `trident_libretro_ios_arm64.dylib` from [Releases](https://github.com/DanAlexMorton/3dsTrident/releases)
3. Transfer the `.dylib` to RetroArch's cores directory on your device:
   - **Via Files app**: Navigate to RetroArch's app folder > `cores/`
   - **Via iTunes/Finder file sharing**: Select the RetroArch app, drop the file into its documents, then move it to `cores/` from within RetroArch's file browser
   - **Via AltStore/sideload tools**: Some tools allow placing files directly into the app sandbox
4. Copy `trident_libretro.info` to RetroArch's `info/` directory
5. Launch RetroArch > Load Core > Trident > Load a 3DS ROM
6. Requires an A11 chip or newer (iPhone 8+, iPad 6th gen+)
7. The iOS build uses the **Metal** renderer — OpenGL is not available on iOS

> **Note**: iOS does not allow JIT compilation on non-jailbroken devices. This may
> affect CPU emulation performance. Shader JIT and fastmem may also be restricted.

## Supported Formats

`.3ds`, `.3dsx`, `.elf`, `.axf`, `.cci`, `.cxi`, `.app`, `.ncch`

## Building from Source

### Prerequisites (all platforms)
- CMake 3.16+
- Git
- A C++20 compiler

### Windows

```bash
git clone --recursive https://github.com/DanAlexMorton/3dsTrident.git
cd 3dsTrident
cmake -B build -G "Visual Studio 17 2022" -A x64 -DBUILD_LIBRETRO_CORE=ON
cmake --build build --config Release --target panda3ds_libretro
```

Output: `build/Release/trident_libretro.dll`

### Linux

```bash
git clone --recursive https://github.com/DanAlexMorton/3dsTrident.git
cd 3dsTrident
sudo apt-get install build-essential cmake libgl-dev libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev
cmake -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_LIBRETRO_CORE=ON
cmake --build build --target panda3ds_libretro -j$(nproc)
```

Output: `build/trident_libretro.so`

### macOS

```bash
git clone --recursive https://github.com/DanAlexMorton/3dsTrident.git
cd 3dsTrident
cmake -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_OSX_ARCHITECTURES=arm64 -DBUILD_LIBRETRO_CORE=ON -DENABLE_METAL=OFF
cmake --build build --target panda3ds_libretro -j$(sysctl -n hw.logicalcpu)
```

Output: `build/trident_libretro.dylib`

### Android

Requires the [Android NDK](https://developer.android.com/ndk/downloads) (r26d recommended).

```bash
git clone --recursive https://github.com/DanAlexMorton/3dsTrident.git
cd 3dsTrident
cmake -B build -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake \
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-26 \
  -DBUILD_LIBRETRO_CORE=ON -DENABLE_METAL=OFF
cmake --build build --target panda3ds_libretro -j$(nproc)
```

Output: `build/trident_libretro.so`

### iOS

Requires Xcode with iOS SDK 14.0+. Must be built on macOS.

```bash
git clone --recursive https://github.com/DanAlexMorton/3dsTrident.git
cd 3dsTrident
cmake -B build -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_SYSTEM_NAME=iOS -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=14.0 -DIOS_SIMULATOR_BUILD=OFF \
  -DCMAKE_C_FLAGS="-march=armv8-a+crc+crypto" \
  -DCMAKE_CXX_FLAGS="-march=armv8-a+crc+crypto" \
  -DBUILD_LIBRETRO_CORE=ON -DENABLE_METAL=ON -DENABLE_OPENGL=OFF
cmake --build build --target panda3ds_libretro -j$(sysctl -n hw.logicalcpu)
```

Output: `build/trident_libretro.dylib`

## License

GPL-3.0 -- see [LICENSE](LICENSE) for details.
