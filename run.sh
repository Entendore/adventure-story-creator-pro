#!/bin/bash
# Adventure Story Creator Pro - Launcher (Linux/Mac)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run setup_project.sh first."
    exit 1
fi

source venv/bin/activate
python src/main.py "$@"
