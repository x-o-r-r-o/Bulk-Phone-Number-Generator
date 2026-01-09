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

echo "Checking for Python $MIN_VERSION+..."

if ! python_ok; then
    echo "Python $MIN_VERSION+ not found. Installing via Homebrew..."

    if ! command_exists brew; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        if [[ -d /opt/homebrew/bin ]]; then
            export PATH="/opt/homebrew/bin:$PATH"
        elif [[ -d /usr/local/bin ]]; then
            export PATH="/usr/local/bin:$PATH"
        fi
    fi

    brew update
    brew install python

    if ! python_ok; then
        echo "Python installation failed. Please install Python manually."
        exit 1
    fi
fi

echo "Running export_e164.py..."
python3 "$SCRIPT" "$@"