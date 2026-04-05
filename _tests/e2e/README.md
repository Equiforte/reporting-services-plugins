# E2E Plugin Tests

Each subdirectory is a test case definition. Tests run in an isolated `_workdir/` directory so no generated files pollute the test definitions.

## How it works

```
_tests/e2e/
├── 01-markdown-default/        # Test definition (committed)
│   ├── prompt.md               #   The prompt to send
│   ├── verify.sh               #   Checks to run after
│   ├── plugins.txt             #   Which plugins to load
│   └── .reporting/             #   (optional) Brand overrides
│
├── _workdir/                   # Runtime output (gitignored)
│   └── 01-markdown-default/    #   Working dir for this test
│       ├── .reporting/         #     Copied from test definition
│       ├── .reporting-resolved/#     Created by brand skill
│       ├── output/             #     Created by generator skill
│       └── claude-output.txt   #     Claude's response
│
└── run_all.sh                  # Test runner
```

## Run tests

```bash
# All tests
bash _tests/e2e/run_all.sh

# Single test
bash _tests/e2e/run_all.sh --test 01

# Re-verify without re-running prompts
bash _tests/e2e/run_all.sh --skip-prompt

# Run one manually
cd _tests/e2e/_workdir/01-markdown-default
claude --plugin-dir ../../../../branding \
       --plugin-dir ../../../../text-generation \
       --dangerously-skip-permissions \
       -p "$(cat ../../01-markdown-default/prompt.md)"
bash ../../01-markdown-default/verify.sh
```

## Inspect results

All output is in `_tests/e2e/_workdir/{test-name}/`:

```bash
# See what Claude generated
cat _tests/e2e/_workdir/01-markdown-default/claude-output.txt

# See the output files
ls _tests/e2e/_workdir/01-markdown-default/output/

# See resolved brand
cat _tests/e2e/_workdir/01-markdown-default/.reporting-resolved/brand-config.json
```
