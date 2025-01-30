#!/bin/sh
cd $(dirname $0)

# Create a virtual environment to run our code
VENV_NAME=".venv"
PYTHON="$VENV_NAME/bin/python"

export PATH=$PATH:$HOME/.local/bin

if ! uv pip install pyinstaller -Uq; then
  exit 1
fi

uv run pyinstaller --onefile --hidden-import="googleapiclient" src/main.py
tar -czvf dist/archive.tar.gz ./dist/main meta.json
