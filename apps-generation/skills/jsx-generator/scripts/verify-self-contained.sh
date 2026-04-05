#!/usr/bin/env bash
set -euo pipefail

# Verify that a built app is fully self-contained.
# Checks for external URLs, CDN references, absolute paths, and required files.
#
# Usage:
#   bash verify-self-contained.sh <dist_dir>
#
# Exit code 0 = pass, 1 = fail

DIST_DIR="${1:?Usage: verify-self-contained.sh <dist_dir>}"
ERRORS=0

echo "Verifying self-containment: $DIST_DIR"
echo "========================================="

# Check required files
echo -n "Checking index.html exists... "
if [[ -f "$DIST_DIR/index.html" ]]; then
  echo "PASS"
else
  echo "FAIL — index.html not found"
  ERRORS=$((ERRORS + 1))
fi

echo -n "Checking assets directory exists... "
if [[ -d "$DIST_DIR/assets" ]]; then
  echo "PASS"
else
  echo "WARN — assets/ directory not found (may be inlined)"
fi

# Check for external URLs in built files
echo -n "Checking for external URLs... "
EXTERNAL_URLS=$(grep -rn 'https\?://' "$DIST_DIR" --include="*.html" --include="*.js" --include="*.css" 2>/dev/null \
  | grep -v 'data:' \
  | grep -v '//# sourceMappingURL' \
  | grep -v 'sourceMap' \
  | grep -v '/\*!' \
  | grep -v 'bit\.ly' \
  | grep -v 'License' \
  | grep -v 'xmlns' \
  | grep -v 'w3\.org' \
  | grep -v 'reactjs\.org' \
  | grep -v 'github\.com' \
  | grep -v 'http://www\.w3\.org' \
  || true)

if [[ -z "$EXTERNAL_URLS" ]]; then
  echo "PASS"
else
  echo "FAIL — external URLs found:"
  echo "$EXTERNAL_URLS" | head -10
  ERRORS=$((ERRORS + 1))
fi

# Check for Google Fonts CDN
echo -n "Checking for Google Fonts CDN... "
GFONTS=$(grep -rn 'fonts.googleapis.com\|fonts.gstatic.com' "$DIST_DIR" --include="*.html" --include="*.css" 2>/dev/null || true)
if [[ -z "$GFONTS" ]]; then
  echo "PASS"
else
  echo "FAIL — Google Fonts CDN reference found:"
  echo "$GFONTS"
  ERRORS=$((ERRORS + 1))
fi

# Check for root-absolute paths (should all be relative ./)
echo -n "Checking for root-absolute paths... "
ROOT_PATHS=$(grep -rn 'src="/' "$DIST_DIR/index.html" 2>/dev/null || true)
ROOT_PATHS+=$(grep -rn 'href="/' "$DIST_DIR/index.html" 2>/dev/null || true)
if [[ -z "$ROOT_PATHS" ]]; then
  echo "PASS"
else
  echo "FAIL — root-absolute paths found in index.html:"
  echo "$ROOT_PATHS"
  ERRORS=$((ERRORS + 1))
fi

# Check for inline scripts that fetch external resources
echo -n "Checking for fetch/XMLHttpRequest to external... "
EXT_FETCH=$(grep -rn "fetch\s*(\s*['\"]https\?://" "$DIST_DIR" --include="*.js" 2>/dev/null || true)
if [[ -z "$EXT_FETCH" ]]; then
  echo "PASS"
else
  echo "FAIL — external fetch calls found:"
  echo "$EXT_FETCH" | head -5
  ERRORS=$((ERRORS + 1))
fi

echo "========================================="
if [[ $ERRORS -eq 0 ]]; then
  echo "RESULT: PASS — app is self-contained"
  exit 0
else
  echo "RESULT: FAIL — $ERRORS issue(s) found"
  exit 1
fi
