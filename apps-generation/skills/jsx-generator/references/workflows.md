# Workflow Suggestions Reference

After generating an app, suggest follow-up workflows to the user based on the template used.

## Dashboard → suggested next steps

- "Export this data as an Excel spreadsheet" → triggers xlsx-generator
- "Create a PDF summary of these KPIs" → triggers pdf-generator
- "Share this as a slide deck" → triggers pptx-generator
- "Update the data" → re-run with new data.json

## Report → suggested next steps

- "Export as PDF" → triggers pdf-generator
- "Export as DOCX" → triggers docx-generator
- "Create a summary dashboard from this report" → triggers jsx-generator (dashboard)

## Comparison → suggested next steps

- "Export this comparison as a table in Excel" → triggers xlsx-generator
- "Add this to a presentation" → triggers pptx-generator
- "Export as PDF one-pager" → triggers pdf-generator

## Timeline → suggested next steps

- "Export milestones as a spreadsheet" → triggers xlsx-generator
- "Create a presentation with this timeline" → triggers pptx-generator
- "Export as Markdown" → triggers text-generator

## Suggestion format

After generating an app, present 2-3 relevant suggestions:

```
Generated: output/app/q1-dashboard/dist/index.html

Next steps you might want:
- Export these KPIs as an Excel spreadsheet
- Create a PDF executive summary
- Build a board deck from this data
```
