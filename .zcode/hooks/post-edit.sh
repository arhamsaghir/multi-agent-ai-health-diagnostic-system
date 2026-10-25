#!/bin/bash
# Post-edit quality and syntax verification hook for ZCode

FILE_PATH="$1"

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Python files: compile check
if [[ "$FILE_PATH" == *.py ]]; then
  if python3 -m py_compile "$FILE_PATH" 2>/dev/null; then
    echo "✓ Python syntax verified: $FILE_PATH"
  else
    echo "✗ Python syntax error in: $FILE_PATH" >&2
    exit 1
  fi
fi

# TypeScript/TSX files: basic check
if [[ "$FILE_PATH" == *.ts || "$FILE_PATH" == *.tsx ]]; then
  if node -c "$FILE_PATH" 2>/dev/null; then
    echo "✓ JS/TS syntax verified: $FILE_PATH"
  fi
fi

exit 0
