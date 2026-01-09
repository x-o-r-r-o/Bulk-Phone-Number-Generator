#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/export_e164.py"

MIN_VERSION=3.8

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

python_ok() {
    if command_exists python3; then
        PY_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        python3 - <<EOF
import sys
min_v = tuple(map(int, "$MIN_VERSION".split(".")))
cur_v = tuple(map(int, "$PY_VER".split(".")))
sys.exit(0 if cur_v >= min_v else 1)
EOF
        return $?
    fi
    return 1
}

install_python() {
    echo "Attempting to install Python 3 via system package manager (requires sudo)..."
    if command_exists apt; then
        sudo apt update
        sudo apt install -y python3 python3-venv python3-pip
    elif command_exists dnf; then
        sudo dnf install -y python3
    elif command_exists yum; then
        sudo yum install -y python3
    elif command_exists zypper; then
        sudo zypper install -y python3
    elif command_exists pacman; then
        sudo pacman -Sy --noconfirm python
    else
        echo "No supported package manager found. Please install Python 3 manually."
        exit 1
    fi
}

echo "Checking for Python $MIN_VERSION+..."

if ! python_ok; then
    install_python
    if ! python_ok; then
        echo "Python installation failed. Please install Python 3 manually."
        exit 1
    fi
fi

echo "Running export_e164.py..."
python3 "$SCRIPT" "$@"