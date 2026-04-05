---
name: orchestration
description: >
  Coordinates multi-format output generation. Triggered when the user requests
  output in multiple formats simultaneously (e.g., "create a PDF and an Excel
  and a dashboard"), or when the user asks to "generate reports in multiple
  formats", "create all outputs", "multi-format export", or requests more than
  one output type in a single message.
---

# Multi-Format Orchestration

When a user requests output in multiple formats, follow this fixed sequence. Do not skip steps. Do not reorder.

## Orchestration sequence

```
1. RESOLVE BRAND     — trigger brand skill → write .reporting-resolved/
2. DATA-FIRST        — generate structured JSON as canonical data source
3. GENERATE          — invoke each generator skill sequentially
4. VALIDATE          — each generator validates its own output
5. SELF-CORRECT      — in strict mode, fix failures (one retry max)
6. SUMMARIZE         — list all produced files with paths and status
```

## Step 1: Resolve brand

Trigger the `brand` skill first. This writes `.reporting-resolved/` with the fully resolved brand config, assets, and office scripts.

**If brand resolution fails** (e.g., invalid JSON in `.reporting/brand-config.json`):
1. Report the specific error with file path and details.
2. Offer to fix the issue if it's a syntax error.
3. **STOP.** Do not invoke any generators. No output without branding.

## Step 2: Data-first (when applicable)

When multiple formats are requested from the same data AND `json-generator` is available (the `text-generation` plugin is installed):

1. Invoke `json-generator` to produce a canonical JSON file.
2. Structure the JSON with all data needed by subsequent generators — KPIs, tables, charts, narrative sections.
3. Write to `output/text/{slug}-{date}-{HHmm}-{xxx}.json`.
4. All subsequent generators read from this file as their canonical data source.

**Why**: This ensures 100% data parity across formats. The PDF, XLSX, and dashboard all render the same numbers because they all read from the same JSON.

**Fallback when `json-generator` is not installed**: Skip this step. Generators use data from the conversation context directly. When generating multiple outputs within the same plugin (e.g., XLSX + CSV), the primary format is generated first and secondary formats are derived from the same in-memory data.

## Step 3: Generate

Invoke each requested generator skill **sequentially**, in the order the user mentioned them. Each generator:

1. Reads brand config from `.reporting-resolved/brand-config.json`.
2. Reads data from the data-first JSON (if available) or conversation context.
3. Produces output in `output/{format}/`.
4. Is independent — no cross-generator dependencies.

## Step 4: Validate

Each generator handles its own validation based on the `mode` setting in `brand-config.json`:

### Mode: `best_effort` (default)

- Warn on issues (missing dependencies, font fallbacks, etc.).
- Produce output anyway.
- No validation sidecars.

### Mode: `strict`

- Hard-fail on: missing required dependency, XLSX formula errors, unresolvable fonts, any validation check failure.
- Emit `{name}.validation.json` sidecar alongside each artifact.
- Sidecar format:

```json
{
  "artifact": "filename.ext",
  "mode": "strict",
  "checks": [
    { "check": "check_name", "status": "pass" | "fail", "detail": "description" }
  ],
  "overall": "pass" | "fail"
}
```

## Step 5: Self-correct (strict mode only)

After each generator produces output in strict mode:

1. Read the `validation.json` sidecar.
2. If `overall` is `"fail"`, attempt to fix the specific failures.
3. Re-generate the artifact.
4. Re-validate.
5. **If validation fails a second time, STOP retrying.** Report the error to the user with details from the sidecar. Do not loop.

This is limited to **one retry** per artifact to prevent infinite correction loops.

## Step 6: Summarize

After all generators have run (or failed), present a summary:

```
Summary: N/M outputs generated.

✓ output/text/q1-data-2026-04-04-1430-c3a.json
✓ output/pdf/q1-executive-summary-2026-04-04-1430-a8f.pdf
✓ output/xlsx/q1-financial-model-2026-04-04-1430-b2c.xlsx
✗ output/pptx/q1-board-deck-2026-04-04-1430-d4e.pptx — PptxGenJS error: ...
✓ output/app/q1-dashboard/dist/

All outputs branded consistently, all sourced from the same data.
```

Include:
- Total success count vs total requested.
- Full file path for each output.
- Error message for any failures.
- Note that all outputs used the same data source (if data-first was used).

## Failure handling rules

| Failure type | Behavior |
|-------------|----------|
| Brand resolution fails | **STOP entirely.** No generators run. Report error, offer to fix. |
| Generator fails | Log error, **continue** with remaining generators. Report partial success. |
| Validation fails (strict, first attempt) | Attempt self-correction — one retry. |
| Validation fails (strict, second attempt) | Report to user with sidecar details. Continue with remaining generators. |
| Missing dependency (best_effort) | Warn and skip that generator. Continue with others. |
| Missing dependency (strict) | Hard-fail that generator. Continue with others. |

## Single-format requests

For single-format requests (e.g., "create a PDF"), the orchestration is simpler:

1. RESOLVE BRAND
2. GENERATE (single generator)
3. VALIDATE (if strict)
4. SELF-CORRECT (if strict and failed)
5. REPORT result

The data-first step is skipped for single-format requests (no cross-format parity needed).
