#!/usr/bin/env bash  
# Тестирование эмулятора с параметром --script.
set -e  
DIR="$(cd "$(dirname "$0")/.." && pwd)"
"$DIR/run.sh" --script "$DIR/samples/demo.esh"
