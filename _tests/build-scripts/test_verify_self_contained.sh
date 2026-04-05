#!/usr/bin/env bash
set -euo pipefail

# Test the verify-self-contained.sh script with good and bad inputs.
#
# Run: bash _tests/build-scripts/test_verify_self_contained.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VERIFY="$REPO_ROOT/apps-generation/skills/jsx-generator/scripts/verify-self-contained.sh"

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

PASSED=0
FAILED=0

pass() { echo "  PASS  $1"; PASSED=$((PASSED + 1)); }
fail() { echo "  FAIL  $1: $2"; FAILED=$((FAILED + 1)); }

# ── Test 1: Valid self-contained dist ──

echo "Test 1: Valid self-contained dist"
mkdir -p "$TMPDIR/good/assets"
cat > "$TMPDIR/good/index.html" << 'EOF'
<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="./assets/index.css"></head>
<body><script src="./assets/index.js"></script></body>
</html>
EOF
echo "body { color: black; }" > "$TMPDIR/good/assets/index.css"
echo "console.log('hello')" > "$TMPDIR/good/assets/index.js"

if bash "$VERIFY" "$TMPDIR/good" > /dev/null 2>&1; then
  pass "valid dist passes"
else
  fail "valid dist passes" "expected exit 0"
fi

# ── Test 2: Missing index.html ──

echo "Test 2: Missing index.html"
mkdir -p "$TMPDIR/no-index/assets"
echo "body {}" > "$TMPDIR/no-index/assets/index.css"

if bash "$VERIFY" "$TMPDIR/no-index" > /dev/null 2>&1; then
  fail "missing index.html" "expected failure"
else
  pass "missing index.html detected"
fi

# ── Test 3: External URL in HTML ──

echo "Test 3: External URL in HTML"
mkdir -p "$TMPDIR/external/assets"
cat > "$TMPDIR/external/index.html" << 'EOF'
<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="https://cdn.example.com/style.css"></head>
<body></body>
</html>
EOF
echo "" > "$TMPDIR/external/assets/index.js"

if bash "$VERIFY" "$TMPDIR/external" > /dev/null 2>&1; then
  fail "external URL" "expected failure"
else
  pass "external URL detected"
fi

# ── Test 4: Google Fonts CDN ──

echo "Test 4: Google Fonts CDN"
mkdir -p "$TMPDIR/gfonts/assets"
cat > "$TMPDIR/gfonts/index.html" << 'EOF'
<!DOCTYPE html>
<html>
<head><link href="./assets/index.css" rel="stylesheet"></head>
<body></body>
</html>
EOF
echo "@import url('https://fonts.googleapis.com/css2?family=Inter');" > "$TMPDIR/gfonts/assets/index.css"

if bash "$VERIFY" "$TMPDIR/gfonts" > /dev/null 2>&1; then
  fail "Google Fonts CDN" "expected failure"
else
  pass "Google Fonts CDN detected"
fi

# ── Test 5: Root-absolute path ──

echo "Test 5: Root-absolute path in HTML"
mkdir -p "$TMPDIR/absolute/assets"
cat > "$TMPDIR/absolute/index.html" << 'EOF'
<!DOCTYPE html>
<html>
<head><link rel="stylesheet" href="/assets/index.css"></head>
<body></body>
</html>
EOF
echo "" > "$TMPDIR/absolute/assets/index.css"

if bash "$VERIFY" "$TMPDIR/absolute" > /dev/null 2>&1; then
  fail "root-absolute path" "expected failure"
else
  pass "root-absolute path detected"
fi

# ── Summary ──

echo ""
echo "$PASSED passed, $FAILED failed"
exit $FAILED
