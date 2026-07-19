#!/usr/bin/env python3
"""
AlphaQuant AI - Build Standalone Executable
============================================
Creates a standalone executable using PyInstaller.
Works on: Windows / macOS / Linux
Run: python build_executable.py

Requirements: pip install pyinstaller
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist" / "AlphaQuant-AI"


def echo(msg: str) -> None:
    print(f">>> {msg}")


def check_deps() -> None:
    """Check that PyInstaller is installed."""
    try:
        import PyInstaller  # noqa: F401
        echo("PyInstaller found OK")
    except ImportError:
        echo("Installing PyInstaller...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            check=True,
        )


def build_frontend() -> None:
    """Build frontend to dist if not already built."""
    dist_dir = PROJECT_ROOT / "frontend" / "dist"
    if dist_dir.is_dir() and list(dist_dir.rglob("*.js")):
        echo("Frontend dist exists, skipping build")
        return
    echo("Building frontend...")
    subprocess.run(
        ["npm", "run", "build"],
        cwd=str(PROJECT_ROOT / "frontend"),
        check=True,
    )


def build_executable() -> None:
    """Build standalone executable with PyInstaller."""
    echo("Building standalone executable (this may take several minutes)...")

    frontend_dist = PROJECT_ROOT / "frontend" / "dist"

    # Clean previous builds
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "--name", "AlphaQuant-AI",
        "--add-data", f"{frontend_dist}{os.pathsep}frontend/dist",
        "--add-data", "requirements.txt.",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "sqlalchemy.ext.asyncio",
        "--hidden-import", "aiosqlite",
        "--hidden-import", "loguru",
        "--hidden-import", "pydantic",
        "--hidden-import", "pydantic_settings",
        "--hidden-import", "python_multipart",
        "--hidden-import", "httpx",
        "--hidden-import", "apscheduler",
        "--collect-submodules", "backend",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--specpath", str(BUILD_DIR),
        str(PROJECT_ROOT / "backend" / "main.py"),
    ]

    subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=True)
    echo(f"Executable built: {DIST_DIR}")


def create_start_script() -> None:
    """Create starter script for the bundled app."""
    system = platform.system()

    if system == "Windows":
        bat_content = """@echo off
echo ============================================================
echo   AlphaQuant AI - Standalone Edition
echo ============================================================
echo.
start "" "AlphaQuant-AI.exe"
echo Server started at http://localhost:8888
echo Press any key to stop server...
pause
"""
        start_script = DIST_DIR / "start.bat"
        start_script.write_text(bat_content, encoding="utf-8")
    else:
        sh_content = """#!/usr/bin/env bash
echo "============================================================"
echo "  AlphaQuant AI - Standalone Edition"
echo "============================================================"
echo ""
./AlphaQuant-AI &
echo "Server started at http://localhost:8888"
echo "Press Enter to stop server..."
read -r
kill %1 2>/dev/null
"""
        start_script = DIST_DIR / "start.sh"
        start_script.write_text(sh_content, encoding="utf-8")
        start_script.chmod(0o755)

    echo(f"Start script created: {start_script}")


def main() -> None:
    echo("=" * 60)
    echo("AlphaQuant AI - Build Executable")
    echo("=" * 60)
    print()

    check_deps()
    build_frontend()
    build_executable()
    create_start_script()

    echo()
    echo(f"Build complete! Find your distribution at: {DIST_DIR}")
    echo("=" * 60)

    system = platform.system()
    if system == "Windows":
        echo("Run: dist\\AlphaQuant-AI\\start.bat")
    else:
        echo("Run: dist/AlphaQuant-AI/start.sh")


if __name__ == "__main__":
    main()
