#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .html file" "ls output/text/*.html >/dev/null 2>&1"
check "has KPI data" "grep -q '12.4' output/text/*.html"
check "has table" "grep -q '<table\|<th' output/text/*.html"
check "self-contained" "! grep -q 'https://' output/text/*.html"
check "has brand colors in CSS" "grep -q '#1B3A5C\|--primary' output/text/*.html"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
