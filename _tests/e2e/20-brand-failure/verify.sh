#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }

# The agent should detect the error — check its output
check "claude detected JSON error" "grep -qi 'error\|invalid\|syntax\|trailing\|parse\|fix' claude-output.txt"
# Should NOT have produced output files
check "no output/text/ created" "[ ! -d output/text ] || [ -z \"\$(ls output/text/ 2>/dev/null)\" ]"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
