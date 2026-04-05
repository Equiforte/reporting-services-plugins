#!/usr/bin/env bash
set -euo pipefail

# Run all tests for the reporting-plugins suite.
#
# Usage:
#   bash _tests/run_all.sh [--profile text-only|documents|full]
#
# Profiles control which tests run:
#   text-only   — brand resolution + schema tests only (no Python deps needed)
#   documents   — + office utility tests (needs Python)
#   full        — + build script tests (needs Node.js)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROFILE="full"

if [[ "${1:-}" == "--profile" ]]; then
  PROFILE="${2:-full}"
fi

TOTAL_PASSED=0
TOTAL_FAILED=0

run_python_tests() {
  local test_file="$1"
  local label="$2"

  echo ""
  echo "═══ $label ═══"

  if python3 "$test_file"; then
    return 0
  else
    return 1
  fi
}

run_bash_tests() {
  local test_file="$1"
  local label="$2"

  echo ""
  echo "═══ $label ═══"

  if bash "$test_file"; then
    return 0
  else
    return 1
  fi
}

echo "Running tests (profile: $PROFILE)"
echo "================================="

# ── Always run: brand resolution ──

run_python_tests "$SCRIPT_DIR/brand-resolution/test_brand_merge.py" "Brand Resolution Tests"

# ── Always run: schema validation ──

run_python_tests "$SCRIPT_DIR/schema-validation/test_schema.py" "Schema Validation Tests"

# ── Documents profile: office utilities ──

if [[ "$PROFILE" == "documents" || "$PROFILE" == "full" ]]; then
  run_python_tests "$SCRIPT_DIR/office-utilities/test_validate.py" "Office Utilities: validate.py (XXE/Security)"
  run_python_tests "$SCRIPT_DIR/office-utilities/test_pack_unpack.py" "Office Utilities: pack/unpack roundtrip"
fi

# ── Full profile: build scripts ──

if [[ "$PROFILE" == "full" ]]; then
  if command -v node &> /dev/null; then
    run_bash_tests "$SCRIPT_DIR/build-scripts/test_verify_self_contained.sh" "Build Scripts: verify-self-contained.sh"
  else
    echo ""
    echo "═══ Build Scripts: SKIPPED (Node.js not installed) ═══"
  fi
fi

echo ""
echo "================================="
echo "Unit tests complete."
echo ""
echo "To run e2e plugin tests (requires Claude Code):"
echo "  bash _tests/e2e/run_all.sh"
echo "  bash _tests/e2e/run_all.sh --test 01   # run single test"
