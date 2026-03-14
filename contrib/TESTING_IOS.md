# Trident -- iOS Testing Plan

Platform: **iOS 14.0+ ARM64**
Core binary: `trident_libretro.dylib`
Frontend: RetroArch (iOS build or sideloaded)
Renderer: **Metal** (OpenGL not available on iOS)

---

## Prerequisites

- iOS device with A11 chip or newer (iPhone 8+, iPad 6th gen+)
- RetroArch sideloaded via AltStore, TrollStore, or developer account
- At least one known-good 3DS ROM for testing
- Enough free storage (~500 MB for RetroArch + core + test ROMs)

---

## 1. Installation & Loading

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 1.1 | Core loads | Place `trident_libretro.dylib` in RetroArch cores directory. Load Core > Trident | Core loads, name shows "Trident" | |
| 1.2 | Core info displays | Information > Core Information | All metadata correct, license GPLv3 | |
| 1.3 | Metal renderer active | Load a game, check logs | Logs show Metal renderer initialized (not OpenGL) | |
| 1.4 | No JIT crash | Load and run a game | Core runs without JIT-related crashes (iOS restricts JIT) | |

## 2. Content Loading

| # | Test | Format | Expected Result | Pass |
|---|------|--------|-----------------|------|
| 2.1 | Decrypted ROM | `.3ds` | Game boots to title screen | |
| 2.2 | Homebrew | `.3dsx` | App boots and runs | |
| 2.3 | CCI image | `.cci` | Game boots to title screen | |
| 2.4 | CXI partition | `.cxi` | Game boots to title screen | |
| 2.5 | NCCH container | `.ncch` | Game boots to title screen | |
| 2.6 | Invalid file | `.txt` | Graceful error, no crash | |

### Recommended test titles

| Title | Why |
|-------|-----|
| New Super Mario Bros. 2 | 2D game, lighter GPU load, good baseline |
| Super Mario 3D Land | 3D graphics stress test |
| The Legend of Zelda: Ocarina of Time 3D | Complex shaders and textures |
| Shovel Knight | 2D with effects, audio testing |

## 3. Metal Renderer

These tests are iOS-specific since the core uses Metal instead of OpenGL.

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 3.1 | Shader compilation | Launch a 3D game | Metal shaders compile without errors in log | |
| 3.2 | Texture rendering | Play through multiple areas with different textures | Textures render correctly, no corruption | |
| 3.3 | Alpha blending | Find transparent UI elements or effects | Transparency renders correctly | |
| 3.4 | Depth buffer | Play 3D game with overlapping geometry | No Z-fighting or depth artifacts beyond normal | |
| 3.5 | Frame output | Check both screens | Top and bottom screens render via Metal | |
| 3.6 | Background/foreground | Switch to another app and back | Core resumes without Metal context loss or crash | |
| 3.7 | Screen rotation | Rotate device | RetroArch handles rotation, core output intact | |

## 4. Input (Touch & Controller)

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 4.1 | On-screen overlay | Enable touch overlay in RetroArch | D-pad, face buttons, shoulders all respond | |
| 4.2 | MFi controller | Connect Bluetooth controller (PS/Xbox/MFi) | All buttons map correctly | |
| 4.3 | Circle Pad analog | Move left stick on controller | Smooth analog input in-game | |
| 4.4 | Touchscreen pointer | Use right stick or direct touch for bottom screen | Pointer registers on 3DS bottom screen | |
| 4.5 | Touch tap | Tap on bottom screen area | Touch input registers in-game | |
| 4.6 | Touch games | Test a game that requires touch (e.g., Professor Layton) | Touch puzzles are solvable | |

## 5. Core Options

| # | Option Key | Test Focus | Pass |
|---|------------|------------|------|
| 5.1 | `trident_use_shader_jit` | May be restricted on iOS (no JIT). Verify behavior when disabled | |
| 5.2 | `trident_use_fastmem` | May be restricted on iOS. Verify no crash on either setting | |
| 5.3 | `trident_dsp_emulation` | Switch between HLE/LLE/Null, verify audio | |
| 5.4 | `trident_use_audio` | Toggle, verify audio on/off | |
| 5.5 | `trident_audio_volume` | Adjust volume levels | |
| 5.6 | `trident_use_ubershader` | Toggle, check for stutter vs performance | |
| 5.7 | `trident_hash_textures` | Toggle, check impact on rendering and performance | |
| 5.8 | `trident_system_language` | Change language, verify in-game | |
| 5.9 | `trident_accurate_shader_mul` | Toggle, test shader-sensitive titles | |
| 5.10 | `trident_use_virtual_sd` | Verify virtual SD works on iOS sandbox | |

## 6. Performance (iOS-specific)

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 6.1 | FPS on 2D game | Load a 2D title, enable FPS counter | Stable ~60 FPS on A11+ | |
| 6.2 | FPS on 3D game | Load a demanding 3D title | Measure FPS, document baseline | |
| 6.3 | Thermal throttling | Play demanding title for 15+ minutes | Document FPS drop if any, device temp | |
| 6.4 | Memory usage | Monitor via Xcode Instruments or in-app | Core stays within iOS memory limits (~1.5 GB) | |
| 6.5 | Battery drain | Play for 30 minutes, note battery % change | Document drain rate | |
| 6.6 | Cold start time | Time from "Load Core" to gameplay | Document load time | |
| 6.7 | Fast-forward | Hold fast-forward | Game speeds up without crash | |

## 7. Save System

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 7.1 | In-game save | Save in-game, close, reload | Save persists in iOS sandbox | |
| 7.2 | Save state | Save state, load state | Restores correctly | |
| 7.3 | Save persistence | Save, close RetroArch entirely, reopen | Saves survive app closure | |
| 7.4 | iCloud conflict | (If applicable) Check save dir isn't in iCloud sync path | No data corruption | |

## 8. RetroAchievements

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 8.1 | Memory exposed | Enable achievements, load supported game | Achievement tracking activates | |
| 8.2 | Achievement unlock | Trigger a known achievement condition | Achievement pops | |

## 9. Stability

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 9.1 | Extended play | Play for 30+ minutes | No crash, no memory leak | |
| 9.2 | App backgrounding | Play, press Home, return to app | Core resumes without crash | |
| 9.3 | Incoming call | Receive a phone call during play | Core pauses, resumes after call | |
| 9.4 | Low memory | Run multiple background apps, then play | Core handles memory pressure gracefully | |
| 9.5 | Rapid load/unload | Load game, close, load different game, repeat 5x | No crashes | |
| 9.6 | Notification | Receive notification banner during play | No crash or rendering glitch | |

## 10. iOS-Specific Edge Cases

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 10.1 | No W^X violation | Run core on non-jailbroken device | Core runs (no JIT code generation that violates iOS policies) | |
| 10.2 | Sandbox paths | Verify save/load paths work within iOS sandbox | Files read/write correctly | |
| 10.3 | AltStore resign | After AltStore 7-day resign cycle | Core still loads and runs | |
| 10.4 | Different devices | Test on iPhone and iPad | Both work, iPad uses available screen space | |

---

## Test Devices

| Device | Chip | iOS Version | Result |
|--------|------|-------------|--------|
| iPhone 15 Pro | A17 Pro | iOS 18.x | |
| iPhone 13 | A15 | iOS 17.x | |
| iPhone SE (3rd) | A15 | iOS 16.x | |
| iPad Air (5th) | M1 | iPadOS 17.x | |
| iPhone 8 (min spec) | A11 | iOS 16.x | |

---

## Sign-Off

| Tester | Date | Device | RetroArch Version | Core Version | Result |
|--------|------|--------|-------------------|--------------|--------|
| | | | | | |
