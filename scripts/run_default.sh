#!/usr/bin/env bash  
# Тестирование эмулятора без параметров командной строки.
set -e  
DIR="$(cd "$(dirname "$0")/.." && pwd)"
"$DIR/run.sh" <<'EOF'
ls  
cd /tmp  
exit  
EOF
