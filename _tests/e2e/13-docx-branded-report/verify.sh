#!/usr/bin/env bash
set -euo pipefail
PASS=0; FAIL=0
check() { if eval "$2"; then echo "    PASS  $1"; PASS=$((PASS+1)); else echo "    FAIL  $1"; FAIL=$((FAIL+1)); fi }
check "has .docx file" "ls output/docx/*.docx >/dev/null 2>&1"
check "DOCX > 5KB" "[ $(stat -f%z output/docx/*.docx 2>/dev/null || stat -c%s output/docx/*.docx 2>/dev/null) -gt 5000 ]"
check "is valid ZIP" "python3 -c \"import zipfile; assert zipfile.is_zipfile('$(ls output/docx/*.docx)')\""
check "has document.xml" "python3 -c \"import zipfile; z=zipfile.ZipFile('$(ls output/docx/*.docx)'); assert 'word/document.xml' in z.namelist()\""
check "brand resolved" "[ -f .reporting-resolved/brand-config.json ]"
echo ""; echo "$PASS passed, $FAIL failed"; [ $FAIL -eq 0 ]
