#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .html file" "ls output/text/*.html >/dev/null 2>&1"
check "self-contained (no https)" "! grep -q 'https://' output/text/*.html"
check "no script tags" "! grep -q '<script' output/text/*.html"
check "has inline CSS" "grep -q '<style>' output/text/*.html"
check "has table" "grep -q '<table' output/text/*.html"
check "has carbon data" "grep -q '15%\|carbon\|emission' output/text/*.html"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
