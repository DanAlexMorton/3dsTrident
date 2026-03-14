# rcheevos Nintendo 3DS Memory Region Support

## Status

An open PR already exists for this: [RetroAchievements/rcheevos#446](https://github.com/RetroAchievements/rcheevos/pull/446)
by CasualPokePlayer. Our Trident libretro core's memory descriptors are
aligned with that PR's virtual-address-based mapping.

## Approach: Virtual Address Mapping

PR #446 maps the 3DS **userland virtual address space** (0x00000000 - 0x3FFFFFFF)
rather than physical addresses. This means game pointers map 1:1 to
RetroAchievements addresses -- critical for 3DS games which are heavily
pointer-driven.

Our Trident core walks Panda3DS's page tables at game load time and builds one
`retro_memory_descriptor` per contiguous physically-backed virtual range.
This provides direct pointers into FCRAM without shadow buffers.

## Key Virtual Memory Regions (from PR #446)

| Virtual Address Range    | Size   | Type              | Description                        |
|--------------------------|--------|-------------------|------------------------------------|
| 0x00100000 - 0x03FFFFFF  | ~63MB  | System RAM        | Code Binary (.code, .data, .bss)   |
| 0x04000000 - 0x07FFFFFF  | 64MB   | Hardware Ctrl     | IPC Buffers                        |
| 0x08000000 - 0x0FFFFFFF  | 128MB  | System RAM        | Regular Heap and Stack             |
| 0x10000000 - 0x13FFFFFF  | 64MB   | Hardware Ctrl     | Shared Memory                      |
| 0x14000000 - 0x1BFFFFFF  | 128MB  | System RAM        | Linear Heap (old base)             |
| 0x1E800000 - 0x1EBFFFFF  | 4MB    | System RAM        | New 3DS Memory                     |
| 0x1F000000 - 0x1F5FFFFF  | 6MB    | Video RAM         | VRAM                               |
| 0x1FF00000 - 0x1FF7FFFF  | 512KB  | Hardware Ctrl     | DSP Memory                         |
| 0x1FF82000 - 0x1FFFFFFF  | ~504KB | System RAM        | Thread Local Storage               |
| 0x30000000 - 0x37FFFFFF  | 128MB  | System RAM        | New Linear Heap                    |
| 0x38000000 - 0x3FFFFFFF  | 128MB  | System RAM        | New Linear Heap (New 3DS only)     |

## References

- 3DS Virtual Memory Layout: https://www.3dbrew.org/wiki/Memory_layout#ARM11_User-land_memory_regions
- Console ID: `RC_CONSOLE_NINTENDO_3DS = 62` (defined in `rc_consoles.h`)
- rcheevos PR: https://github.com/RetroAchievements/rcheevos/pull/446
