#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .json file" "ls output/text/*.json >/dev/null 2>&1"
check "valid JSON" "python3 -c \"import json; json.load(open('$(ls output/text/*.json)'))\" 2>/dev/null"
check "has meta section" "python3 -c \"import json; d=json.load(open('$(ls output/text/*.json)')); assert 'meta' in d\""
check "has data or kpis" "python3 -c \"import json; d=json.load(open('$(ls output/text/*.json)')); assert 'data' in d or 'kpis' in d\""
check "has ARR data" "grep -q 'ARR\|14.8' output/text/*.json"
check "pretty-printed" "grep -q '  ' output/text/*.json"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
