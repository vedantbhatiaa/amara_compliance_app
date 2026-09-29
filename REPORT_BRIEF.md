# Site-visit report extraction brief

You are extracting the legal-compliance content from dss+ site-visit reports (PDF) for the client
Amara NZero, so it can be shown in an interactive dashboard. Root folder:
`/home/claude/src/Amara_NZero/05. Sent_To_Client/02. Site Visits/`

Tools: `pdftotext -layout -f N -l N file.pdf -` for text; `pdftoppm -r 80 -png -f N -l N -singlefile file.pdf /tmp/claude-0/-home-claude/1e87adab-253c-59de-8d2a-96c87e9de9ce/scratchpad/<name>`
then Read the PNG to see a page (needed to read the coloured compliance dots and any text that is an image).
First get an outline of all pages with pdftotext, then only look closely at the relevant pages:
- Executive summary (strengths / areas for improvement / key findings)
- "Key Activities" / "Legal and Regulatory Compliance Review" / "Actividades clave" pages — tables listing each
  key activity, its related regulations, a compliance indicator (coloured dot or label) and comments / missing items
- "Quick wins and recommendations" (compliance part; include safety-culture quick wins only if on the same page)

Compliance dot colours: green = "Compliant", orange/amber = "Partially compliant", red = "Non-compliant",
grey/none = "Not assessed". If the table uses words instead of dots, map them to those four values.

## Output
Write ONE JSON file per site to `/home/claude/build/reports/<SITE_ID>.json` using a Python script
(json.dump, ensure_ascii=False, indent=1). Schema:

```json
{
  "site_id": "ES-VAL",
  "report_file": "2026_06_Site_Visit_Report_Valencia.pdf",
  "report_language": "en",            
  "visit_date": "April 2026 (as stated, or empty)",
  "summary_strengths":   [{"en": "...", "orig": "..."}],
  "summary_improvements":[{"en": "...", "orig": "..."}],
  "key_activities": [
    {"activity": {"en": "Load at height", "orig": "..."},
     "regulations": ["RD 1215/1997", "..."],
     "status": "Compliant | Partially compliant | Non-compliant | Not assessed",
     "comments": [{"en": "Risk assessment taking into account RD 1215/1997 ... is missing", "orig": "..."}]}
  ],
  "quick_wins":      [{"en": "...", "orig": "..."}],
  "recommendations": [{"en": "...", "orig": "..."}]
}
```
- `orig` = the text exactly as in the report (original language). `en` = English. If the report is already in
  English, `en` and `orig` are identical.
- Translate Spanish/French/Italian/Portuguese faithfully into professional English H&S terminology; keep legal
  citations (RD 486/1997, NOM-030-STPS-2009, Decreto 1072/2015 ...) and site/company names unchanged.
- Capture every key activity row in the report's key-activities tables (usually 6–20). Keep comment bullets
  complete (do not summarise), one list item per bullet / numbered point.
- If a section does not exist in the report, use an empty list. Do not invent content.
- When one report covers two sites (noted below), split content by site into two files; content that applies to
  both goes in both.
- Validate each file loads with json.load before finishing.

Reply with one line per file written: site id, number of key activities, number of strengths/improvements/quick wins.
