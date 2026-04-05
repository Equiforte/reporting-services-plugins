#!/usr/bin/env bash
set -euo pipefail

# Run all e2e tests sequentially.
# Each test: cd into dir, run prompt via claude, then verify.
#
# Usage:
#   bash _tests/e2e/run_all.sh [--test NN] [--skip-prompt]
#
# Options:
#   --test NN       Run only test NN (e.g., --test 01)
#   --skip-prompt   Skip the Claude prompt, only run verify.sh (for re-checking)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WORKDIR_ROOT="$SCRIPT_DIR/_workdir"
ONLY_TEST=""
SKIP_PROMPT=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --test) ONLY_TEST="$2"; shift 2 ;;
    --skip-prompt) SKIP_PROMPT=true; shift ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

PASSED=0
FAILED=0
SKIPPED=0

for test_dir in "$SCRIPT_DIR"/[0-9][0-9]-*/; do
  test_name=$(basename "$test_dir")
  test_num="${test_name%%-*}"

  if [[ -n "$ONLY_TEST" && "$test_num" != "$ONLY_TEST" ]]; then
    continue
  fi

  echo ""
  echo "════════════════════════════════════════════"
  echo "TEST: $test_name"
  echo "════════════════════════════════════════════"

  if [[ ! -f "$test_dir/prompt.md" ]]; then
    echo "  SKIP — no prompt.md"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Create isolated working directory for this test run
  work="$WORKDIR_ROOT/$test_name"
  rm -rf "$work"
  mkdir -p "$work"

  # Copy test setup files (.reporting/ overrides, data files) into work dir
  if [[ -d "$test_dir/.reporting" ]]; then
    cp -r "$test_dir/.reporting" "$work/.reporting"
  fi

  # Determine which plugins this test needs
  PLUGIN_ARGS="--plugin-dir $REPO_ROOT/branding"

  if [[ -f "$test_dir/plugins.txt" ]]; then
    while IFS= read -r plugin; do
      [[ -z "$plugin" || "$plugin" == \#* ]] && continue
      PLUGIN_ARGS="$PLUGIN_ARGS --plugin-dir $REPO_ROOT/$plugin"
    done < "$test_dir/plugins.txt"
  else
    for p in text-generation document-generation spreadsheet-generation presentation-generation apps-generation; do
      [[ -d "$REPO_ROOT/$p" ]] && PLUGIN_ARGS="$PLUGIN_ARGS --plugin-dir $REPO_ROOT/$p"
    done
  fi

  # Run the prompt from the work directory
  if [[ "$SKIP_PROMPT" == false ]]; then
    echo "  Working dir: $work"
    echo "  Running prompt..."
    PROMPT=$(cat "$test_dir/prompt.md")
    # shellcheck disable=SC2086
    (cd "$work" && claude $PLUGIN_ARGS --dangerously-skip-permissions -p "$PROMPT" --output-format text > claude-output.txt 2>&1) || true
    echo "  Claude finished. Output saved to $work/claude-output.txt"
  else
    echo "  Skipping prompt (--skip-prompt)"
  fi

  # Run verification from the work directory
  if [[ -f "$test_dir/verify.sh" ]]; then
    echo "  Verifying..."
    if (cd "$work" && bash "$test_dir/verify.sh"); then
      echo "  RESULT: PASS"
      PASSED=$((PASSED + 1))
    else
      echo "  RESULT: FAIL"
      FAILED=$((FAILED + 1))
    fi
  else
    echo "  SKIP — no verify.sh"
    SKIPPED=$((SKIPPED + 1))
  fi
done

echo ""
echo "════════════════════════════════════════════"
echo "SUMMARY: $PASSED passed, $FAILED failed, $SKIPPED skipped"
echo "════════════════════════════════════════════"
exit $FAILED
