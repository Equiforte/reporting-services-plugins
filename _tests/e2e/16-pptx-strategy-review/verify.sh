#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .pptx file" "ls output/pptx/*.pptx >/dev/null 2>&1"
check "PPTX > 15KB" "[ $(stat -f%z output/pptx/*.pptx 2>/dev/null || stat -c%s output/pptx/*.pptx 2>/dev/null) -gt 15000 ]"
check "has 6+ slides" "python3 -c \"import zipfile; z=zipfile.ZipFile('$(ls output/pptx/*.pptx)'); slides=[n for n in z.namelist() if 'slides/slide' in n and n.endswith('.xml')]; assert len(slides) >= 6, f'{len(slides)} slides'\""
check "brand resolved with Globex" "grep -q 'Globex' .reporting-resolved/brand-config.json"
check "brand primary green" "grep -q '006633' .reporting-resolved/brand-config.json"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
