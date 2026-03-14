# rcheevos Nintendo 3DS Memory Region Contribution

This document describes the changes needed in the [rcheevos](https://github.com/RetroAchievements/rcheevos)
library to add proper Nintendo 3DS memory region support, replacing the current
compatibility-mode fallback.

## File: `src/rcheevos/consoleinfo.c`

### 1. Add memory region definition (after Nintendo DSi, before Oric)

```c
/* ===== Nintendo 3DS ===== */
/* https://www.3dbrew.org/wiki/Memory_layout */
static const rc_memory_region_t _rc_memory_regions_nintendo_3ds[] = {
  { 0x00000000U, 0x07FFFFFFU, 0x20000000U, RC_MEMORY_TYPE_SYSTEM_RAM, "FCRAM" },
  { 0x08000000U, 0x085FFFFFU, 0x18000000U, RC_MEMORY_TYPE_VIDEO_RAM, "VRAM" }
};
static const rc_memory_regions_t rc_memory_regions_nintendo_3ds = { _rc_memory_regions_nintendo_3ds, 2 };
```

### 2. Add switch case in `rc_console_memory_regions()` (after Nintendo DSi)

```c
    case RC_CONSOLE_NINTENDO_3DS:
      return &rc_memory_regions_nintendo_3ds;
```

## Memory Layout Rationale

| RA Address Range        | Size  | Hardware Address | Type       | Description |
|------------------------|-------|------------------|------------|-------------|
| 0x00000000 - 0x07FFFFFF | 128MB | 0x20000000       | System RAM | FCRAM       |
| 0x08000000 - 0x085FFFFF | 6MB   | 0x18000000       | Video RAM  | VRAM        |

- **FCRAM** (Fast Capture RAM): The primary system memory where game code, data,
  heap, and stack reside. This is the most important region for achievement
  development. Physical address range: 0x20000000 - 0x27FFFFFF.

- **VRAM** (Video RAM): GPU video memory used for textures, framebuffers, and
  rendering data. Physical address range: 0x18000000 - 0x185FFFFF.

## Core Compatibility

The Panda3DS libretro core exposes these regions via `RETRO_ENVIRONMENT_SET_MEMORY_MAPS`
with matching physical addresses, and also provides `retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM)`
returning the FCRAM pointer for compatibility-mode fallback.

## References

- 3DS Memory Layout: https://www.3dbrew.org/wiki/Memory_layout
- Console ID: `RC_CONSOLE_NINTENDO_3DS = 62` (already defined in `rc_consoles.h`)
- 3DS hashing support already exists in `rc_hash.c`
