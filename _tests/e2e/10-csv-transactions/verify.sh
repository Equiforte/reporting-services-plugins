#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .csv file" "ls output/csv/*.csv >/dev/null 2>&1"
check "has 20+ rows" "[ $(wc -l < output/csv/*.csv) -ge 20 ]"
check "has TXN IDs" "grep -q 'TXN-' output/csv/*.csv"
check "has categories" "grep -q 'Sales\|Marketing\|Operations' output/csv/*.csv"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
