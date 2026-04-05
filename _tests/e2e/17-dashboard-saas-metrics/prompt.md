First resolve branding (run the brand skill to write .reporting-resolved/), then: Build an interactive dashboard for SaaS metrics. Data:
- KPIs: ARR $14.8M (+22%), NRR 118% (+3pp), CAC Payback 14 months (-2mo), LTV/CAC 4.2x (+0.5x)
- Area chart: ARR growth monthly Jan-Jun 2026: $12.1M, $12.5M, $13.0M, $13.6M, $14.2M, $14.8M
- Bar chart: New MRR vs Churned MRR by month (Jan-Jun): New [85K, 92K, 78K, 95K, 110K, 105K], Churned [22K, 18K, 25K, 20K, 15K, 19K]
- Table: Cohort retention (Jan 2025: M1 100%, M3 92%, M6 85%, M12 78%)

Use the dashboard template with sidebar, shadcn cards, and Recharts. Write to output/app/ directory.

IMPORTANT: When running npm commands, use a local cache to avoid permission issues: set the environment variable npm_config_cache to a .npm-cache directory in the current working directory (e.g., export npm_config_cache=./.npm-cache).
