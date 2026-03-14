# Trident -- Windows Testing Plan

Platform: **Windows 10/11 x64**
Core binary: `trident_libretro.dll`
Frontend: RetroArch (latest stable)

---

## 1. Installation & Loading

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 1.1 | Core loads in RetroArch | Place `trident_libretro.dll` in RetroArch `cores/`. Launch RetroArch > Load Core > Trident | Core loads without crash, name shows as "Trident" | |
| 1.2 | Core info displays | Information > Core Information | display_name, version, license (GPLv3), supported extensions all shown correctly | |
| 1.3 | Core appears in Online Updater | (Post-buildbot) Online Updater > Core Downloader | "Nintendo - 3DS (Trident)" listed | |

## 2. Content Loading

Test with at least one title per format. Use a known-good commercial dump or homebrew.

| # | Test | Format | Expected Result | Pass |
|---|------|--------|-----------------|------|
| 2.1 | Decrypted ROM | `.3ds` | Game boots to title screen | |
| 2.2 | Homebrew | `.3dsx` | App boots and runs | |
| 2.3 | ELF binary | `.elf` | Binary executes | |
| 2.4 | AXF binary | `.axf` | Binary executes | |
| 2.5 | CCI image | `.cci` | Game boots to title screen | |
| 2.6 | CXI partition | `.cxi` | Game boots to title screen | |
| 2.7 | NCCH container | `.ncch` | Game boots to title screen | |
| 2.8 | App format | `.app` | Game boots to title screen | |
| 2.9 | Invalid file | `.txt` | Graceful error, no crash | |
| 2.10 | Missing file | Load nonexistent path | Graceful error, no crash | |

### Recommended test titles

| Title | Format | Why |
|-------|--------|-----|
| Super Mario 3D Land | `.3ds` | 3D graphics, good GPU stress test |
| The Legend of Zelda: A Link Between Worlds | `.3ds` | Complex shaders, dual screen usage |
| Mario Kart 7 | `.3ds` | Multiplayer/online stubs, 3D rendering |
| Shovel Knight | `.3ds` | 2D with effects, audio-heavy |
| 3DSX Homebrew Launcher | `.3dsx` | Validates homebrew path |

## 3. Input

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 3.1 | D-pad | Press all 4 directions | Corresponding 3DS input registers | |
| 3.2 | Face buttons | Press A, B, X, Y | Correct mapping (A=A, B=B, X=X, Y=Y) | |
| 3.3 | Shoulder buttons | Press L1, R1 | Maps to 3DS L/R | |
| 3.4 | Triggers | Press L2, R2 | Maps to 3DS ZL/ZR | |
| 3.5 | Start/Select | Press Start, Select | Correct mapping | |
| 3.6 | Circle Pad | Move left analog stick | Smooth analog movement in-game | |
| 3.7 | Touchscreen via right stick | Move right analog stick + R3 | Pointer moves on bottom screen, R3 taps | |
| 3.8 | Input remapping | Remap A to B in RetroArch | Remapped input works correctly | |

## 4. Core Options

Verify each option applies correctly. Toggle each, restart if needed, confirm behavior.

| # | Option Key | Values | Test Method | Pass |
|---|------------|--------|-------------|------|
| 4.1 | `trident_use_shader_jit` | enabled / disabled | Toggle, observe shader compile speed | |
| 4.2 | `trident_accelerate_shaders` | enabled / disabled | Toggle, check for rendering changes | |
| 4.3 | `trident_accurate_shader_mul` | disabled / enabled | Enable, test known shader-sensitive game | |
| 4.4 | `trident_use_ubershader` | enabled / disabled | Toggle, observe stutter reduction | |
| 4.5 | `trident_use_vsync` | enabled / disabled | Toggle, observe tearing | |
| 4.6 | `trident_hash_textures` | enabled / disabled | Toggle, check texture rendering fidelity | |
| 4.7 | `trident_system_language` | En/Fr/Es/De/... | Change, reboot game, verify language | |
| 4.8 | `trident_dsp_emulation` | HLE / LLE / Null | Switch, verify audio output changes | |
| 4.9 | `trident_use_audio` | enabled / disabled | Disable, confirm silence | |
| 4.10 | `trident_audio_volume` | 0-200 | Set to 0, 100, 200, verify volume levels | |
| 4.11 | `trident_mute_audio` | disabled / enabled | Mute, confirm silence | |
| 4.12 | `trident_enable_aac` | enabled / disabled | Toggle, test game with AAC audio tracks | |
| 4.13 | `trident_use_virtual_sd` | enabled / disabled | Disable, verify games needing SD fail gracefully | |
| 4.14 | `trident_write_protect_virtual_sd` | disabled / enabled | Enable, attempt save on SD, verify failure | |
| 4.15 | `trident_battery_level` | 5-100 | Set to 5, check in-game battery indicator | |
| 4.16 | `trident_use_charger` | enabled / disabled | Toggle, check in-game charging status | |
| 4.17 | `trident_use_fastmem` | enabled / disabled | Toggle, verify no crashes on either setting | |
| 4.18 | `trident_ubershader_lighting_override` | enabled / disabled | Toggle in light-heavy scene | |
| 4.19 | `trident_ubershader_lighting_override_threshold` | 1-8 | Adjust, observe rendering in lit scenes | |

## 5. Save System

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 5.1 | In-game save | Save in a game, close, reload | Save persists | |
| 5.2 | Save state create | Quick Menu > Save State | State saved without crash | |
| 5.3 | Save state load | Quick Menu > Load State | State restores correctly | |
| 5.4 | Save state across sessions | Save state, close RetroArch, reopen, load state | Restores correctly | |
| 5.5 | Multiple save slots | Save to slots 0, 1, 2, load each | Each slot restores independently | |

## 6. RetroAchievements

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 6.1 | Memory exposed | Load game in RALibretro, open Memory Inspector | Memory regions visible, regions match 3DS virtual address space | |
| 6.2 | Memory readable | Read known memory addresses | Values change as expected during gameplay | |
| 6.3 | Hash identification | Load a supported title | Game is identified (hash matches) | |

## 7. Video & Audio

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 7.1 | Both screens render | Load any game | Top and bottom screens visible | |
| 7.2 | Correct aspect ratio | Check output dimensions | No stretching or distortion | |
| 7.3 | 60 FPS target | Enable FPS counter (Settings > On-Screen Display) | Shows ~60 FPS on a capable machine | |
| 7.4 | Audio plays | Load game with music | Audio output present, no crackling | |
| 7.5 | Audio sync | Play for 5+ minutes | No audio drift or desync | |
| 7.6 | RetroArch shaders | Apply a CRT shader | Shader renders over core output without artifacts | |
| 7.7 | Screenshot | Take screenshot via RetroArch | Screenshot captured correctly | |
| 7.8 | Recording | Start FFmpeg recording, play 30s, stop | Video file plays back correctly | |

## 8. Stability

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 8.1 | Extended play | Play a game for 30+ minutes | No crashes or memory leaks | |
| 8.2 | Rapid load/unload | Load game, close, load different game, repeat 10x | No crashes | |
| 8.3 | Core restart | Quick Menu > Restart | Game restarts cleanly | |
| 8.4 | Rewind | Enable rewind, hold rewind button | Gameplay rewinds smoothly (if supported) | |
| 8.5 | Fast-forward | Hold fast-forward button | Game runs faster without crash | |
| 8.6 | Slow-motion | Enable slow motion | Game runs at reduced speed without crash | |

## 9. Edge Cases

| # | Test | Steps | Expected Result | Pass |
|---|------|-------|-----------------|------|
| 9.1 | No content loaded | Try to run core without content | Graceful error (supports_no_game = false) | |
| 9.2 | Path with spaces | Load ROM from `C:\My Games\3DS\game.3ds` | Loads successfully | |
| 9.3 | Path with unicode | Load ROM from path with non-ASCII characters | Loads or fails gracefully | |
| 9.4 | Very long path | Load ROM from deeply nested directory | Loads or fails gracefully | |

---

## Sign-Off

| Tester | Date | RetroArch Version | Core Version | Result |
|--------|------|-------------------|--------------|--------|
| | | | | |
