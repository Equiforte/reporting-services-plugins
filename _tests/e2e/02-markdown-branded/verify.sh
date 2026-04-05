#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }

check "has .md file" "ls output/text/*.md >/dev/null 2>&1"
check "mentions Globex" "grep -qi 'globex' output/text/*.md"
check "has revenue data" "grep -q '25' output/text/*.md"
check "brand resolved" "[ -f .reporting-resolved/brand-config.json ]"
check "resolved has Globex" "grep -q 'Globex' .reporting-resolved/brand-config.json"
check "resolved primary is green" "grep -q '006633' .reporting-resolved/brand-config.json"
check "logo suppressed" "[ ! -f .reporting-resolved/logo.png ]"

echo ""; echo "$PASS passed, $FAIL failed"
[ $FAIL -eq 0 ]
