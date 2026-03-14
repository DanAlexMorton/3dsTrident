# Trident -- Libretro Buildbot Submission Guide

This document covers everything needed to submit the Trident 3DS core to the
libretro buildbot via [libretro-super](https://github.com/libretro/libretro-super).

Source repository: <https://github.com/DanAlexMorton/3dsTrident>

---

## Pre-Submission Checklist

- [x] Core builds and runs in RetroArch
- [x] `.gitlab-ci.yml` in repo root (used by libretro's GitLab CI buildbot)
- [x] `trident_libretro.info` in repo root (core metadata for RetroArch)
- [x] `GIT_SUBMODULE_STRATEGY: recursive` set (required -- Panda3DS is a submodule)
- [x] `CORENAME: trident` matches output binary name (`trident_libretro.so/.dll/.dylib`)
- [x] `is_experimental = "true"` in info file (appropriate for new cores)
- [x] GitHub Actions CI passing on all target platforms
- [ ] **Submit info file** to `libretro-super/dist/info/`
- [ ] **Submit recipe entries** to `libretro-super/recipes/` (per-platform)
- [ ] **Request GitLab mirror** of the repo under `libretro/` org (or fork to `libretro/`)
- [ ] **Verify GitLab CI** runs successfully on the mirrored repo

---

## 1. Info File for libretro-super

Copy the contents below to `libretro-super/dist/info/trident_libretro.info`:

```ini
# Software Information
display_name = "Nintendo - 3DS (Trident)"
authors = "Trident Contributors"
supported_extensions = "3ds|3dsx|elf|axf|cci|cxi|app|ncch"
corename = "Trident"
categories = "Emulator"
license = "GPLv3"
permissions = ""
display_version = "Git"

# Hardware Information
manufacturer = "Nintendo"
systemname = "3DS"
systemid = "3ds"

# Libretro Information
database = "Nintendo - Nintendo 3DS"
supports_no_game = "false"
savestate = "true"
savestate_features = "basic"
cheats = "false"
input_descriptors = "true"
memory_descriptors = "true"
libretro_saves = "true"
core_options = "true"
core_options_version = "1.0"
load_subsystem = "false"
hw_render = "true"
required_hw_api = "OpenGL Core >= 4.1 | Metal"
needs_fullpath = "true"
disk_control = "false"
is_experimental = "true"

description = "A 3DS libretro core powered by the Panda3DS emulation engine."
```

This is identical to the `trident_libretro.info` already in this repository.

---

## 2. Recipe Entries for libretro-super

The libretro-super buildbot uses per-platform recipe files. Each line follows this format:

```
{CORENAME} {COREDIR} {URL} {BRANCH} {ENABLED} {COMMAND} {MAKEFILE} {SUBDIR} {ARGS}
```

Once the repo is mirrored/forked to `libretro/`, the URL below should be updated
to point to `https://github.com/libretro/trident.git` (or whatever the mirror name is).

### Linux x86_64 (`recipes/linux/cores-linux-x64-generic`)

```
trident libretro-trident https://github.com/libretro/trident.git main YES CMAKE Makefile build -DBUILD_LIBRETRO_CORE=ON -DUSE_LIBRETRO_AUDIO=ON -DENABLE_USER_BUILD=ON -DENABLE_VULKAN=OFF -DENABLE_LUAJIT=OFF -DENABLE_DISCORD_RPC=OFF -DENABLE_QT_GUI=OFF -DENABLE_OPENGL=ON -DENABLE_HTTP_SERVER=OFF -DENABLE_TESTS=OFF
```

### Android ARM64 (`recipes/android/cores-android-aarch64`)

```
trident libretro-trident-aarch64 https://github.com/libretro/trident.git main YES CMAKE Makefile build -DBUILD_LIBRETRO_CORE=ON -DUSE_LIBRETRO_AUDIO=ON -DENABLE_USER_BUILD=ON -DENABLE_VULKAN=OFF -DENABLE_LUAJIT=OFF -DENABLE_DISCORD_RPC=OFF -DENABLE_QT_GUI=OFF -DENABLE_OPENGL=ON -DENABLE_HTTP_SERVER=OFF -DENABLE_TESTS=OFF -DANDROID_ABI=arm64-v8a -DCMAKE_BUILD_TYPE=Release
```

> **Note:** The primary build system for the libretro buildbot is **GitLab CI**,
> not these recipe files. The `.gitlab-ci.yml` already in this repo handles all
> platform builds. Recipe entries are used by the older `libretro-super` build
> scripts and for users building cores locally with `libretro-buildbot-recipe.sh`.

---

## 3. GitLab CI (already done)

The `.gitlab-ci.yml` at the repository root is configured for the libretro
buildbot's GitLab CI infrastructure. It uses the `libretro-infrastructure/ci-templates`
project and builds for:

| Platform        | CI Template                    | Job Name                         |
|-----------------|--------------------------------|----------------------------------|
| Linux x64       | `linux-cmake.yml`              | `libretro-build-linux-x64`       |
| Windows x64     | `windows-cmake-mingw.yml`      | `libretro-build-windows-x64`     |
| macOS x86_64    | `osx-cmake-x86.yml`            | `libretro-build-osx-x64`         |
| macOS ARM64     | `osx-cmake-arm64.yml`          | `libretro-build-osx-arm64`       |
| Android ARM64   | `android-cmake.yml`            | `android-arm64-v8a`              |
| iOS ARM64       | `ios-cmake.yml`                | `libretro-build-ios-arm64`       |

No changes needed here -- the file will be picked up automatically when the repo
is mirrored to libretro's GitLab instance.

---

## 4. How to Submit

### Step 1: Open a PR to libretro-super

1. Fork <https://github.com/libretro/libretro-super>
2. Add the info file:
   - Copy `trident_libretro.info` to `dist/info/trident_libretro.info`
3. Add recipe lines (append to each platform recipe file):
   - `recipes/linux/cores-linux-x64-generic`
   - `recipes/android/cores-android-aarch64`
   - (Add to other platform recipes as needed)
4. Commit and open a pull request
5. In the PR description, link to this repo and note that the `.gitlab-ci.yml`
   is already present for the GitLab buildbot

### Step 2: Request a GitLab mirror

The libretro buildbot runs on GitLab. The repo needs to be mirrored (or forked)
under the `libretro` organization on GitLab:

- Contact the libretro team on Discord (`#development` channel) or open an issue
  at <https://github.com/libretro/libretro-super/issues>
- Request that `https://github.com/DanAlexMorton/3dsTrident` be mirrored to
  `https://git.libretro.com/libretro/trident` (or similar)
- Once mirrored, the GitLab CI will automatically pick up `.gitlab-ci.yml`
  and start building

### Step 3: Verify builds

After the mirror is set up:

1. Check the GitLab CI pipeline at `https://git.libretro.com/libretro/trident/-/pipelines`
2. Verify all 6 platform builds succeed
3. Confirm the built cores appear on the libretro buildbot nightly page

---

## 5. Useful Links

- libretro-super: <https://github.com/libretro/libretro-super>
- CI templates: <https://git.libretro.com/libretro-infrastructure/ci-templates>
- Buildbot: <https://buildbot.libretro.com/>
- libretro Discord: <https://discord.gg/libretro>
- Recipe format reference: `libretro-super/recipes/recipes.info`
- Reference core (citra): `libretro-super/dist/info/citra_libretro.info`
