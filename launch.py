#!/usr/bin/env python3
"""
AlphaQuant AI - Cross-platform One-Click Launcher
=================================================
Supports: Windows / macOS / Linux
Requires: Python 3.11+
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
VENV_DIR = PROJECT_ROOT / ".venv"
ENV_FILE = PROJECT_ROOT / ".env"
ENV_PROD_FILE = PROJECT_ROOT / ".env.production"

COLOR_CODES = {
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "cyan": "\033[96m",
    "reset": "\033[0m",
}


def echo(msg: str, color: str = "cyan") -> None:
    c = COLOR_CODES.get(color, COLOR_CODES["cyan"])
    print(f"{c}>>> {msg}{COLOR_CODES['reset']}")


def check_python() -> None:
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 11):
        echo(f"Need Python 3.11+, current: {v.major}.{v.minor}.{v.micro}", "red")
        echo("Download from https://www.python.org/downloads/", "red")
        sys.exit(1)
    echo(f"Python {v.major}.{v.minor}.{v.micro} OK", "green")


def setup_venv() -> Path:
    if VENV_DIR.exists():
        echo(f"Virtual env exists: {VENV_DIR}", "green")
    else:
        echo("Creating virtual environment...", "cyan")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        echo("Virtual env created OK", "green")
    return VENV_DIR


def get_python_exe() -> str:
    if platform.system() == "Windows":
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python")


def get_pip_exe() -> str:
    if platform.system() == "Windows":
        return str(VENV_DIR / "Scripts" / "pip.exe")
    return str(VENV_DIR / "bin" / "pip")


def install_deps() -> None:
    pip = get_pip_exe()
    req = PROJECT_ROOT / "requirements.txt"
    if not req.exists():
        echo("requirements.txt not found", "red")
        return
    echo("Installing Python dependencies...", "cyan")
    subprocess.run(
        [pip, "install", "--upgrade", "pip"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run([pip, "install", "-r", str(req)], check=True)
    echo("Dependencies installed OK", "green")


def build_frontend() -> None:
    dist = FRONTEND_DIR / "dist"
    if dist.is_dir() and list(dist.rglob("*.js")):
        echo("Frontend dist exists, skipping OK", "green")
        return
    npm = shutil.which("npm")
    if not npm:
        echo("Node.js/npm not found, API-only mode", "yellow")
        return
    echo("Installing frontend dependencies...", "cyan")
    subprocess.run(
        [npm, "install"],
        cwd=str(FRONTEND_DIR),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    echo("Building frontend...", "cyan")
    subprocess.run([npm, "run", "build"], cwd=str(FRONTEND_DIR), check=True)
    echo("Frontend build OK", "green")


def ensure_env() -> None:
    if ENV_FILE.exists():
        echo(f"Config {ENV_FILE.name} exists OK", "green")
        return
    if ENV_PROD_FILE.exists():
        shutil.copy2(str(ENV_PROD_FILE), str(ENV_FILE))
        echo(f"Created config from {ENV_PROD_FILE.name} OK", "green")
    else:
        lines = [
            "# AlphaQuant AI - Standalone Config",
            "APP_NAME=AlphaQuant AI",
            "ENVIRONMENT=development",
            "DEBUG=false",
            "API_PREFIX=/api/v1",
            "HOST=0.0.0.0",
            "PORT=8888",
            "TIMEZONE=Asia/Shanghai",
            "JWT_SECRET_KEY=alphaquant-prod-secret-change-me",
            "ACCESS_TOKEN_EXPIRE_MINUTES=1440",
            "RATE_LIMIT_ENABLED=false",
            "DATABASE_ENGINE=sqlite",
            "DATABASE_URL=sqlite+aiosqlite:///./alphaquant.db",
            "LOG_LEVEL=INFO",
            "DEEPSEEK_API_KEY=",
            "SCHEDULER_ENABLED=false",
            "WEBSOCKET_ENABLED=false",
        ]
        ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        echo("Created default .env config OK", "green")


def start_server() -> subprocess.Popen:
    pye = get_python_exe()
    echo("Starting AlphaQuant AI server...", "cyan")
    return subprocess.Popen(
        [
            pye, "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8888",
            "--log-level", "info",
        ],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def wait_for_server(url: str, timeout: int = 30) -> bool:
    import urllib.request
    echo(f"Waiting for server (up to {timeout}s)...", "cyan")
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url + "/api/v1/health", timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def open_browser(url: str) -> None:
    echo(f"Opening browser: {url}", "cyan")
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main() -> None:
    print()
    echo("=" * 60, "cyan")
    echo("  AlphaQuant AI - Stock Analysis Platform", "cyan")
    echo("  One-Click Launcher (Windows / macOS / Linux)", "cyan")
    echo("=" * 60, "cyan")
    print()

    check_python()
    setup_venv()
    install_deps()
    build_frontend()
    ensure_env()

    url = "http://localhost:8888"
    proc = start_server()

    try:
        if wait_for_server(url):
            echo("Server is running!", "green")
            echo(f"  Local:   {url}", "green")
            echo(f"  API Doc: {url}/docs", "green")
            print()
            open_browser(url)
            print()
            echo("Press Ctrl+C to stop the server", "yellow")
            echo("=" * 60, "cyan")
            print()
            for line in proc.stdout:
                print(line, end="")
        else:
            echo("Server startup timed out, check logs", "red")
            echo(f"Manual: {get_python_exe()} -m uvicorn backend.main:app --host 0.0.0.0 --port 8888", "yellow")
    except KeyboardInterrupt:
        echo("\nShutting down server...", "yellow")
        proc.terminate()
        proc.wait()
        echo("Server stopped OK", "green")

    echo("\nThank you for using AlphaQuant AI!", "cyan")


if __name__ == "__main__":
    main()
