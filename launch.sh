#!/usr/bin/env bash
# AlphaQuant AI - Unix/macOS Launcher
set -e

echo "============================================================"
echo "  AlphaQuant AI - Stock Analysis Platform"
echo "  Unix/macOS Launcher"
echo "============================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found! Please install Python 3.11+"
    echo "Download from https://www.python.org/downloads/"
    exit 1
fi

# Run launcher
cd "$(dirname "$0")"
python3 launch.py

