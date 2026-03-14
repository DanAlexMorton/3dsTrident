"""
Functional tests for the Trident libretro core using libretro.py.

These tests exercise the core's libretro API contract without
requiring RetroArch or a GPU context. They validate:
  - API version compatibility
  - System info metadata (name, extensions, flags)
  - Init/deinit lifecycle
  - Memory region exposure (FCRAM)
  - Serialization interface
"""

import pytest
from libretro import Core
from libretro.api import API_VERSION

RETRO_MEMORY_SYSTEM_RAM = 2
RETRO_MEMORY_SAVE_RAM = 0
FCRAM_SIZE = 0x08000000  # 128 MB


class TestAPIVersion:
    def test_api_version_matches(self, core: Core):
        assert core.api_version() == API_VERSION


class TestSystemInfo:
    def test_library_name(self, core: Core):
        info = core.get_system_info()
        assert info.library_name == b"Trident"

    def test_valid_extensions_include_3ds(self, core: Core):
        info = core.get_system_info()
        assert info.valid_extensions is not None
        assert b"3ds" in info.valid_extensions

    def test_valid_extensions_include_3dsx(self, core: Core):
        info = core.get_system_info()
        assert b"3dsx" in info.valid_extensions

    def test_valid_extensions_include_elf(self, core: Core):
        info = core.get_system_info()
        assert b"elf" in info.valid_extensions

    def test_valid_extensions_include_cci(self, core: Core):
        info = core.get_system_info()
        assert b"cci" in info.valid_extensions

    def test_valid_extensions_include_cxi(self, core: Core):
        info = core.get_system_info()
        assert b"cxi" in info.valid_extensions

    def test_need_fullpath(self, core: Core):
        info = core.get_system_info()
        assert info.need_fullpath

    def test_library_version_not_empty(self, core: Core):
        info = core.get_system_info()
        assert info.library_version is not None
        assert len(info.library_version) > 0


class TestInitDeinit:
    def test_init_deinit_no_crash(self, session_builder):
        with session_builder.build() as session:
            pass

    def test_double_session(self, core_path):
        """Two sequential sessions should not crash."""
        from libretro import SessionBuilder

        for _ in range(2):
            builder = SessionBuilder(core=str(core_path)).with_content(None)
            with builder.build() as session:
                pass


class TestMemory:
    def test_system_ram_size(self, session_builder):
        with session_builder.build() as session:
            size = session.core.get_memory_size(RETRO_MEMORY_SYSTEM_RAM)
            assert size == FCRAM_SIZE, f"Expected {FCRAM_SIZE:#x}, got {size:#x}"

    def test_system_ram_data_not_null(self, session_builder):
        with session_builder.build() as session:
            ptr = session.core.get_memory_data(RETRO_MEMORY_SYSTEM_RAM)
            assert ptr is not None

    def test_system_ram_memoryview(self, session_builder):
        with session_builder.build() as session:
            mem = session.core.get_memory(RETRO_MEMORY_SYSTEM_RAM)
            if mem is not None:
                assert len(mem) == FCRAM_SIZE

    def test_save_ram_size_zero_without_game(self, session_builder):
        with session_builder.build() as session:
            size = session.core.get_memory_size(RETRO_MEMORY_SAVE_RAM)
            assert size == 0


class TestSerialization:
    def test_serialize_size(self, session_builder):
        with session_builder.build() as session:
            size = session.core.serialize_size()
            # May be 0 if save states are not implemented
            assert isinstance(size, int)
            assert size >= 0
