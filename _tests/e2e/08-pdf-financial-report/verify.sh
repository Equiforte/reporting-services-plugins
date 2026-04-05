#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .pdf file" "ls output/pdf/*.pdf >/dev/null 2>&1"
check "PDF > 1KB" "[ $(stat -f%z output/pdf/*.pdf 2>/dev/null || stat -c%s output/pdf/*.pdf 2>/dev/null) -gt 1000 ]"
check "valid PDF" "head -c 5 output/pdf/*.pdf | grep -q '%PDF-'"
check "brand resolved with FinCorp" "grep -q 'FinCorp' .reporting-resolved/brand-config.json"
check "primary is dark" "grep -q '1A1A2E' .reporting-resolved/brand-config.json"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
