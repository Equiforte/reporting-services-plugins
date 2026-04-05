---
name: design-system
description: >
  Provides design system tokens, component patterns, and language guidelines for
  report output. Triggered when the agent needs to look up color tokens, typography
  rules, component styling, number formatting, table patterns, chart palettes,
  or terminology guidelines for any output format. Also triggered when the user
  asks about "design system", "brand tokens", "component styles", or "formatting rules".
---

# Design System

Reference system for all generators. Consult these references when producing any output format to ensure cross-format visual consistency.

## How to use

1. Read `.reporting-resolved/brand-config.json` for the resolved token values.
2. Consult `references/tokens.md` for how to map tokens to specific format contexts.
3. Consult `references/components.md` for reusable visual patterns (tables, cards, charts).
4. Consult `references/language.md` for terminology, disclaimers, and confidence labels.

Always use the resolved brand values — never hardcode colors, fonts, or sizes.
