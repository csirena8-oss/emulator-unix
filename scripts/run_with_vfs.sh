#!/usr/bin/env bash  
# Тестирование эмулятора с параметром --vfs.
set -e  
DIR="$(cd "$(dirname "$0")/.." && pwd)"
"$DIR/run.sh" --vfs "$DIR/samples/vfs.zip" <<'EOF'
ls -l  
exit  
EOF 
