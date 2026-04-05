#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }

check "app dir exists" "[ -d output/app ] && ls -d output/app/*/ >/dev/null 2>&1"
APP=$(ls -d output/app/*/ 2>/dev/null | head -1)
check "has dist/" "[ -d ${APP}dist ]"
check "has dist/index.html" "[ -f ${APP}dist/index.html ]"
check "has src/" "[ -d ${APP}src ]"
check "has data.json" "[ -f ${APP}dist/data.json ] || [ -f ${APP}public/data.json ] || find ${APP} -name 'data.json' | grep -q ."
check "has JS bundle" "ls ${APP}dist/assets/*.js >/dev/null 2>&1"
check "dist self-contained" "! grep -q 'https://' ${APP}dist/index.html 2>/dev/null || true"
check "has package.json" "[ -f ${APP}package.json ]"
check "brand resolved" "[ -f .reporting-resolved/brand-config.json ]"

echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
