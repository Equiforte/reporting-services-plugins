#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .pptx file" "ls output/pptx/*.pptx >/dev/null 2>&1"
check "PPTX > 10KB" "[ $(stat -f%z output/pptx/*.pptx 2>/dev/null || stat -c%s output/pptx/*.pptx 2>/dev/null) -gt 10000 ]"
check "is valid ZIP" "python3 -c \"import zipfile; assert zipfile.is_zipfile('$(ls output/pptx/*.pptx)')\""
check "has slides" "python3 -c \"import zipfile; z=zipfile.ZipFile('$(ls output/pptx/*.pptx)'); slides=[n for n in z.namelist() if 'slides/slide' in n and n.endswith('.xml')]; assert len(slides) >= 4, f'only {len(slides)} slides'\""
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
