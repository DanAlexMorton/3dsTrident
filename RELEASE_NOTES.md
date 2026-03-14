# Trident v1.0.0 -- Release Notes

**Date**: March 2026
**Core**: Trident 3DS Libretro Core
**Engine**: Panda3DS
**License**: GPL-3.0

---

## What is Trident?

Trident is a Nintendo 3DS emulator packaged as a libretro core. It runs inside
RetroArch (and other libretro frontends) on 6 platforms. Built on the Panda3DS
emulation engine, it brings 3DS emulation to the libretro ecosystem with
RetroAchievements support as a first-class feature.

---

## Highlights

### 6-Platform Support

| Platform | Renderer | Status |
|----------|----------|--------|
| Windows x64 | OpenGL | Supported |
| Linux x64 | OpenGL | Supported |
| macOS ARM64 (Apple Silicon) | OpenGL | Supported |
| macOS x64 (Intel) | OpenGL | Supported |
| Android ARM64 | OpenGL ES | Experimental |
| iOS ARM64 | OpenGL ES | Experimental |

### RetroAchievements Ready

- Full 3DS virtual address space exposed via `RETRO_ENVIRONMENT_SET_MEMORY_MAPS`
- Memory descriptors walk the ARM11 page tables to expose all mapped regions
- Compatible with RALibretro for achievement development and testing
- Game hashing support via rcheevos (contribution prepared)

### Core Options

19 configurable options accessible from RetroArch's Quick Menu:

- **Rendering**: Shader JIT, ubershaders, shader acceleration, accurate
  multiplication, texture hashing
- **Audio**: DSP emulation mode (HLE/LLE/Null), volume control, AAC support,
  mute toggle
- **System**: Language selection, virtual SD card, battery level, charger status
- **Performance**: Fastmem, VSync, ubershader lighting overrides

### Supported Formats

`.3ds`, `.3dsx`, `.elf`, `.axf`, `.cci`, `.cxi`, `.app`, `.ncch`

---

## Technical Details

### Rendering

- Desktop platforms use **OpenGL 4.1+**
- Android uses **OpenGL ES 3.2**
- iOS uses **OpenGL ES 3.0** (same rendering path as Android)
- Dual-screen output composited into a single framebuffer

### Audio

- 32768 Hz sample rate
- HLE (fast) and LLE (accurate) DSP emulation modes
- AAC audio decoding via fdk-aac
- Volume scaling from 0% to 200%

### Input

- Full RetroPad mapping: D-pad, A/B/X/Y, L/R, ZL/ZR, Start/Select
- Circle Pad via left analog stick
- Touchscreen input via right analog stick + R3
- Input remapping supported through RetroArch

### Save System

- In-game saves persist across sessions
- Save states supported
- Multiple save state slots

---

## Known Limitations

- **iOS JIT**: iOS does not allow JIT on non-jailbroken devices, which may
  impact CPU emulation performance
- **Encrypted ROMs**: Decrypted ROM dumps are required; encrypted content is
  not supported
- **Stereoscopic 3D**: The 3DS stereoscopic 3D effect is not emulated
- **Local multiplayer**: Not supported
- **Microphone**: Not currently implemented via libretro
- **Camera**: Not currently implemented via libretro
- **Amiibo**: Not currently supported
- **Android/iOS**: Marked as experimental — performance and stability may vary
  by device

---

## Build & CI

- Automated builds via GitHub Actions for all 6 platforms
- GitLab CI configuration ready for the libretro buildbot
- Submission PR to libretro-super: [#1964](https://github.com/libretro/libretro-super/pull/1964)

---

## What's Next

- Performance optimization for mobile platforms
- Upstream rcheevos contribution for 3DS console ID and hash support
- Core documentation for libretro-docs
- Automated functional testing via libretro.py

---

## Credits

- [Panda3DS](https://github.com/wheremyfoodat/Panda3DS) by wheremyfoodat and
  contributors — the emulation engine powering Trident
- [libretro](https://www.libretro.com/) — the API and ecosystem
- [RetroArch](https://www.retroarch.com/) — the reference frontend
- [RetroAchievements](https://retroachievements.org/) — the achievement platform

---

## Links

- **Source**: https://github.com/DanAlexMorton/3dsTrident
- **Releases**: https://github.com/DanAlexMorton/3dsTrident/releases
- **CI**: https://github.com/DanAlexMorton/3dsTrident/actions
- **libretro-super PR**: https://github.com/libretro/libretro-super/pull/1964
