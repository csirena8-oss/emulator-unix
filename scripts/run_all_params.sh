#!/usr/bin/env bash  
# Тестирование эмулятора со всеми параметрами командной строки.
set -e  
DIR="$(cd "$(dirname "$0")/.." && pwd)"
"$DIR/run.sh" \
    --vfs "$DIR/samples/vfs.zip" \
    --script "$DIR/samples/demo.esh"
