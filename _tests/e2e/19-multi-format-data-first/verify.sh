#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has JSON" "ls output/text/*.json >/dev/null 2>&1"
check "has PDF" "ls output/pdf/*.pdf >/dev/null 2>&1"
check "has CSV" "ls output/csv/*.csv >/dev/null 2>&1"
check "JSON has 12.4" "grep -q '12.4\|12400000' output/text/*.json"
check "CSV has 12.4" "grep -q '12.4\|12400000' output/csv/*.csv"
check "PDF exists" "[ -f output/pdf/*.pdf ]"
check "brand resolved" "[ -f .reporting-resolved/brand-config.json ]"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
