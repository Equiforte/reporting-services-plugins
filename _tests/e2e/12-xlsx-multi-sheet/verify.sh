#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .xlsx file" "ls output/xlsx/*.xlsx >/dev/null 2>&1"
check "XLSX > 5KB" "[ $(stat -f%z output/xlsx/*.xlsx 2>/dev/null || stat -c%s output/xlsx/*.xlsx 2>/dev/null) -gt 5000 ]"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
