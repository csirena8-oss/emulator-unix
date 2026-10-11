#!/usr/bin/env bash  
# Запуск эмулятора оболочки (Вариант 25).
set -e  
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
exec python3 -m src.shell_emulator "$@"
