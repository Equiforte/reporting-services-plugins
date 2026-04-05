#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .csv file" "ls output/csv/*.csv >/dev/null 2>&1"
check "has header row" "head -1 output/csv/*.csv | grep -qi 'name\|customer'"
check "has 5+ data rows" "[ $(wc -l < output/csv/*.csv) -ge 6 ]"
check "has Alice" "grep -q 'Alice' output/csv/*.csv"
check "has Eva" "grep -q 'Eva' output/csv/*.csv"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
