#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }

check "output/text/ exists" "[ -d output/text ]"
check "has .md file" "ls output/text/*.md >/dev/null 2>&1"
check "has YAML frontmatter" "head -1 output/text/*.md | grep -q '^---'"
check "has title in frontmatter" "grep -q 'title:' output/text/*.md"
check "has confidential flag" "grep -q 'confidential' output/text/*.md"
check "has revenue data" "grep -q '12.4' output/text/*.md"
check "has table" "grep -q '|' output/text/*.md"
check ".reporting-resolved/ created" "[ -d .reporting-resolved ]"
check "brand-config.json resolved" "[ -f .reporting-resolved/brand-config.json ]"

echo ""; echo "$PASS passed, $FAIL failed"
[ $FAIL -eq 0 ]
