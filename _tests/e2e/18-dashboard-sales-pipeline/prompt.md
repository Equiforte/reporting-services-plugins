First resolve branding (run the brand skill to write .reporting-resolved/), then: Create an interactive sales pipeline dashboard. Data:
- KPIs: Pipeline Value $42.3M (+15%), Win Rate 28% (+3pp), Avg Deal Size $85K (+12%), Sales Cycle 62 days (-8d)
- Bar chart: Pipeline by stage — Prospect $15.2M, Qualified $10.8M, Proposal $8.5M, Negotiation $5.3M, Closed Won $2.5M
- Table: Top 3 deals — "Enterprise Platform" TechCorp $1.2M Negotiation, "Cloud Migration" FinServ $850K Proposal, "Analytics Suite" RetailCo $620K Qualified

Use the dashboard template with sidebar and shadcn components. Write to output/app/ directory.

IMPORTANT: When running npm commands, use a local cache to avoid permission issues: set the environment variable npm_config_cache to a .npm-cache directory in the current working directory (e.g., export npm_config_cache=./.npm-cache).
