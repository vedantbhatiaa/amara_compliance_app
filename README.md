# Amara NZero · Legal Compliance Dashboard (Streamlit)

> Continuing the project? Start with **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)**: requirements, decisions, data rules and open items.

Interactive version of the dss+ Safety, Legal Compliance & Culture Assessment results (June 2026).

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```
Opens at http://localhost:8501. No internet or API key is needed (the Montserrat web font loads if online; otherwise a system font is used).

## What's inside

| Tab | Content | Data source |
|---|---|---|
| ① Legal requirements | Filters (region, country, type of business, free-text search), KPIs, treemap of where requirements sit, most-referenced regulations, key-activity cards with their regulations, Excel-style register (no criticality / no results) with Excel/CSV export | 23 site checklists (1,002 requirements) |
| ② Site compliance | Region → Country → Site drop-downs; site banner and KPIs; compliance-by-criticality chart; key compliance gaps; status donut; compliance by key activity; site-visit report assessment table (activity, regulations, status dot, comments); strengths / improvements / quick wins / recommendations; full assessed checklist with filters and export | Deck site charts + checklists + site-visit reports |
| ③ Cluster results | The cluster of the site chosen in tab ②: business type × criticality chart, high-critical gaps panel, per-site small multiples, compliance mix by type of business, % compliant heatmap | Global & cluster presentations |
| ④ Global · high criticality | Deck chart of high-criticality results by business type and cluster (with flags), gaps panel, one chart per cluster, mix per cluster / per business type, all-criticality comparison, executive summary | Global results presentation |

**Translate switch (top right, applies to every tab):** *Original* shows checklist and report text in the
source language (Spanish, French, Italian, Portuguese); *English* shows a full English translation.
Translations are pre-computed and bundled in `data/translations_en.json` (4,443 strings), so switching is
instant and works offline. Deck content (tabs ③–④ and the key-gap panels) was published in English.

## Data notes
- **Clusters** follow the decks: Spain & Portugal, Mexico & Colombia, France, Greece & Italy.
- **Chart figures** in tabs ②–④ are the officially reported deck numbers. Where a site has no chart in
  the deck (Iberdrola, Schneider, Braskem — reported together — and the remote Chetumal / Altamira
  assessments), tab ② computes the chart from the checklist and says so under the chart.
- **Status normalisation** (checklist tables): Cumplido/Conforme/Cumple → Compliant; Parcial… → Partially
  compliant; No conforme / Pendiente (evidence pending) → Non-compliant; No aplica / No relevante / N/A →
  Not applicable. The two France checklists record status as cell colour; it was read from the colour.
- France office criticality uses the reviewed "Niveau de criticité AA" column.
- Chetumal and Altamira checklists came from the Amara NZero site-visit folder (not the working-files folder).

## Files
```
app.py            Streamlit app (layout, tabs, styling)
charts.py         Plotly figures in the deck style
core.py           data loading, translation helpers, palette, flags
data/             checklist.json · translations_en.json · deck_results.json · site_reports.json · header_labels.json
assets/           dss+ and Amara NZero logos
data_prep/        scripts used to build data/ from the source Excel files and decks
```
