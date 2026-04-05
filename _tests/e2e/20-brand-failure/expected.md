# Expected: FAILURE

The .reporting/brand-config.json has a trailing comma (invalid JSON).
Brand resolution should fail. The agent should:
1. Report the JSON syntax error
2. Offer to fix it
3. NOT produce any output files
