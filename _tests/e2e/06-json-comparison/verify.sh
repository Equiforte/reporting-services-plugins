#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .json file" "ls output/text/*.json >/dev/null 2>&1"
check "valid JSON" "python3 -c \"import json; json.load(open('$(ls output/text/*.json)'))\" 2>/dev/null"
check "has Starter" "grep -q 'Starter' output/text/*.json"
check "has Pro" "grep -q 'Pro' output/text/*.json"
check "has Enterprise" "grep -q 'Enterprise' output/text/*.json"
check "has pricing" "grep -q '29\|99\|499' output/text/*.json"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
