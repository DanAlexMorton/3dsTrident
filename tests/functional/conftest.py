"""
Pytest fixtures for Trident libretro core functional tests.

The core binary path is resolved from:
  1. TRIDENT_CORE_PATH environment variable (used in CI)
  2. Auto-detection in common build directories
"""

import os
import platform
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent


def _detect_core_path() -> Path | None:
    """Auto-detect the core binary in common build output locations."""
    system = platform.system()
    if system == "Windows":
        ext = "dll"
        candidates = [
            REPO_ROOT / "build" / "Release" / f"trident_libretro.{ext}",
            REPO_ROOT / "build" / f"trident_libretro.{ext}",
        ]
    elif system == "Darwin":
        ext = "dylib"
        candidates = [
            REPO_ROOT / "build" / f"trident_libretro.{ext}",
        ]
    else:
        ext = "so"
        candidates = [
            REPO_ROOT / "build" / f"trident_libretro.{ext}",
        ]

    for p in candidates:
        if p.exists():
            return p
    return None


def pytest_addoption(parser):
    parser.addoption(
        "--core",
        action="store",
        default=None,
        help="Path to the trident_libretro core binary",
    )


@pytest.fixture(scope="session")
def core_path(request) -> Path:
    """Resolve the path to the Trident core shared library."""
    path_str = request.config.getoption("--core") or os.environ.get("TRIDENT_CORE_PATH")
    if path_str:
        p = Path(path_str).resolve()
    else:
        p = _detect_core_path()

    if not p or not p.exists():
        pytest.skip(f"Core binary not found (tried: {p}). Set TRIDENT_CORE_PATH or pass --core.")

    return p


@pytest.fixture(scope="session")
def core(core_path):
    """Load the core via libretro.py and return a Core instance."""
    from libretro import Core

    return Core(str(core_path))


@pytest.fixture(scope="session")
def session_works(core_path) -> bool:
    """Probe once whether a libretro session can be created.

    Session creation may fail in headless CI environments that lack
    an OpenGL context (the Trident core requires one during init).
    """
    from libretro import SessionBuilder

    try:
        builder = SessionBuilder(core=str(core_path)).with_content(None)
        with builder.build():
            pass
        return True
    except Exception:
        return False


@pytest.fixture
def session_builder(core_path, session_works):
    """Return a SessionBuilder pre-configured for the Trident core (no content).

    Skips the test if session creation is not possible (e.g. no GPU).
    """
    if not session_works:
        pytest.skip("Session requires OpenGL context (not available in headless CI)")

    from libretro import SessionBuilder

    return SessionBuilder(core=str(core_path)).with_content(None)
