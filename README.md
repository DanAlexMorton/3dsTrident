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
| iOS ARM64 | Experimental | OpenGL ES 3.0 | `trident_libretro.dylib` |

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

> **Important**: iOS does not allow loading `.dylib` files at runtime. You cannot
> simply drop a core file into a folder like on desktop platforms. The Trident core
> must be built into RetroArch's app bundle and code-signed together.

**Option A -- Build RetroArch with Trident from source (recommended):**

1. Clone RetroArch and Trident on a Mac with Xcode installed:
   ```bash
   git clone --recursive https://github.com/libretro/RetroArch.git
   git clone --recursive https://github.com/DanAlexMorton/3dsTrident.git
   ```
2. Build the Trident core for iOS (see [Building from Source > iOS](#ios-1) below)
3. Copy the built `trident_libretro.dylib` into the RetroArch Xcode project's core bundle
4. Build and sign RetroArch with Xcode, deploying to your device
5. The core will appear in Load Core > Trident

**Option B -- Sideload via AltStore / Sideloadly:**

1. Build RetroArch with Trident included (same as Option A steps 1-3)
2. Export a signed `.ipa` from Xcode
3. Install via [AltStore](https://altstore.io/) or [Sideloadly](https://sideloadly.io/)

> AltStore-signed apps must be refreshed every 7 days unless you have a paid
> Apple Developer account ($99/year).

**Requirements:**
- A Mac with Xcode (for building)
- An A11 chip or newer (iPhone 8+, iPad 6th gen+)
- iOS does not allow JIT compilation on non-jailbroken devices, which may
  affect CPU emulation performance

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
  -DBUILD_LIBRETRO_CORE=ON -DENABLE_OPENGL=ON -DOPENGL_PROFILE=OpenGLES \
  -DENABLE_METAL=OFF
cmake --build build --target panda3ds_libretro -j$(sysctl -n hw.logicalcpu)
```

Output: `build/trident_libretro.dylib`

## License

GPL-3.0 -- see [LICENSE](LICENSE) for details.
