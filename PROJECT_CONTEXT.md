# PROJECT CONTEXT — Amara NZero Legal Compliance Dashboard

> **Read this first.** This file is the handoff brief for any person or AI agent continuing the project.
> It holds the original requirements, every decision taken so far, how the data was built, the code layout,
> known quirks, and what is still open. Keep it updated when you change behaviour.

---

## 1. What this is

A **Streamlit (Python)** dashboard that presents the results of the **dss+ "Safety, Legal Compliance & Culture
Assessment"** delivered to the client **Amara NZero** in June 2026. The results were already shared with the client as
Excel checklists, PDF site-visit reports and PDF cluster/global presentations. This app represents the same
results interactively.

- Owner: Vedant Bhatia (Data Scientist intern, dss+ London)
- Repo: https://github.com/vedantbhatiaa/amara_compliance_app
- Status: **v0.2**: v0.1 draft plus a UI round (header, navigation, page 1 redesign); more changes to come (see §10).
- Run: `pip install -r requirements.txt` → `streamlit run app.py` → http://localhost:8501
- Tested with Python 3.11, Streamlit 1.64, Plotly 7.1, pandas 3.0. Needs Streamlit ≥ 1.50 (`pip install -U streamlit`).

---

## 2. Original requirements (from the brief)

1. **Four tabs**, each a dashboard of several charts that fit together and are easy to read:
   1. **Identification of legal requirements**: a general overview listing all legal requirements in a table
      (like the Excel checklists), **without criticality levels** and **without the site-assessment columns**
      (the last Excel columns hold site results, so leave them out).
   2. **Site drill-down**: the user picks **region (cluster) → country → site** from drop-downs to dive into
      site-, region- and country-specific records, with data visualisation as well as the table.
      Seven countries: Colombia, France, Greece, Italy, Mexico, Portugal, Spain. Spain and Mexico have many sites;
      France and Colombia have two each.
   3. **Cluster results**: show **only the cluster of the selected company/site**, with graphs structured like the
      deck (Office / EPC / Factory / Warehouse / Services × High / Medium / Low criticality).
   4. **Global, highest criticality**: Factory / EPC / Warehouse / Office / Services across countries.
      Include one combined all-clusters chart **and** separate high-criticality charts per cluster.
2. Tables in tabs 1–2 must look **Excel-style** (rows and columns, scrolling).
3. **Translate switch at the top right, always visible on every tab**, with **only two options: Original and
   English**. The English translation must be accurate (legal and H&S terminology).
4. **Theme, style and colours** come from the dss+ / Amara NZero PPT graphs and the screenshots.
5. Keep the useful legal-compliance information from the **site-visit reports** (the "Identification of Key
   Activities & Legal Requirements" and "Legal Compliance Assessment" slides: activity, regulations, compliance
   dot, comments).
6. Ask before guessing on anything ambiguous.

### Decisions confirmed with the owner (Q&A)
| Question | Decision |
|---|---|
| Cluster grouping (the brief's example paired Spain with France) | **Use the deck clusters**: Spain & Portugal · Mexico & Colombia · France · Greece & Italy |
| Chart numbers: deck figures or recomputed from Excel (they differ) | **Deck figures for charts**; Excel feeds the tables and activity-level breakdowns |
| Chetumal & Altamira (in the Amara NZero zip, not in the working-files zip) | **Include them** as Mexico sites |
| Translation approach | **Pre-translated and bundled** (no runtime API, works offline) |

---

## 3. Source material (NOT in the repo; confidential client data)

The raw inputs were uploaded as three zips. They are **not committed** and are needed only to rebuild `data/`.
- `excel_working_files_without_translation.zip`: 21 site checklists (.xlsx, national languages)
- `Amara_NZero.zip` → `05. Sent_To_Client/`
  - `01. Identification of legal requirements/2026-04-21_Requisitos_legales_Amara_NZero.pdf`
  - `02. Site Visits/<country>/<site>/`: site-visit report PDFs (+ checklist xlsx; Chetumal & Altamira xlsx come from here)
  - `03. Cluster Presentation/`: 4 cluster decks (PDF)
  - `04. Global results presentation/2026_06_AmaraNZero_Global_Results_Presentation.pdf`
- `cluster.zip`: the same 4 cluster decks

Key deck pages: Global deck pp.12–13 = high criticality by business type & cluster; pp.14–19 = per-cluster
business×criticality charts; p.8 = executive summary. Cluster decks: "Compliance Status by Criticality: <site>"
slides (Spain/PT pp.7,9–16; MX/CO pp.7,9–13; FR pp.7,9; GR/IT pp.7,9).

> ⚠️ The repo is currently **public** and contains client data (checklists, deck figures, report extracts)
> that the decks mark **Confidential**. Consider making it private.

---

## 4. Sites (23)

| site_id | Site | Country | Cluster | Business type | Checklist lang | Rows |
|---|---|---|---|---|---|---|
| ES-MAD | Madrid Office | Spain | Spain & Portugal | Office | es | 31 |
| ES-MEC | Meco Warehouse | Spain | Spain & Portugal | Warehouse | es | 78 |
| ES-SEV | Sevilla Warehouse | Spain | Spain & Portugal | Warehouse | es | 78 |
| ES-VAL | Valencia Warehouse | Spain | Spain & Portugal | Warehouse | es | 78 |
| ES-AND | Andoain Warehouse (CavyCar) | Spain | Spain & Portugal | Warehouse | es | 58 |
| ES-BUR | Burgos Warehouse | Spain | Spain & Portugal | Warehouse | es | 72 |
| ES-VIT | Vitoria Factory (CavyCar) | Spain | Spain & Portugal | Factory | es | 81 |
| ES-ACO | A Coruña – Repsol in-house warehouse | Spain | Spain & Portugal | Services | es | 11 |
| PT-AVE | Aveiro Office | Portugal | Spain & Portugal | Office | pt | 45 |
| MX-MTY | Monterrey Warehouse (owned) | Mexico | Mexico & Colombia | Warehouse | es | 81 |
| MX-CDMX | CDMX Office | Mexico | Mexico & Colombia | Office | es | 47 |
| MX-INO | EPC INOAC | Mexico | Mexico & Colombia | EPC | es | 38 |
| MX-IBE | Iberdrola in-house warehouse | Mexico | Mexico & Colombia | Services | es | 17 |
| MX-BRA | Braskem in-house warehouse | Mexico | Mexico & Colombia | Services | es | 17 |
| MX-SCH | Schneider general services (Monterrey) | Mexico | Mexico & Colombia | Services | es | 25 |
| MX-CHE | Chetumal general services | Mexico | Mexico & Colombia | Services | es | 25 |
| MX-ALT | Altamira – Quantum warehouse & services | Mexico | Mexico & Colombia | Services | es | 17 |
| CO-HOM | Home-office (teleworking) | Colombia | Mexico & Colombia | Office | es | 21 |
| CO-EPC | EPC Solar project | Colombia | Mexico & Colombia | EPC | es | 49 |
| FR-OFF | Villeurbanne Office | France | France | Office | fr | 30 |
| FR-EPC | EPC – subcontractor & logistics | France | France | EPC | fr | 31 |
| GR-ATH | Athens Office | Greece | Greece & Italy | Office | en | 28 |
| IT-BUC | Buccinasco Office (HQ) | Italy | Greece & Italy | Office | it | 44 |

Total: 1,002 checklist rows. "Services" = Amara staff working in client-operated (in-house) warehouses and sites.

---

## 5. Architecture

```
app.py            Streamlit UI: CSS theme, header + translate switch, 4 tabs
charts.py         Plotly figure builders in the deck style
core.py           load_all() (st.cache_resource), T()/RT()/translate_df() translation helpers,
                  palette, SVG flags, KPI/panel HTML helpers, split_regulations(), counts_from_checklist()
data/             pre-built JSON (below)
assets/           dss+ and Amara NZero logos (extracted from the global deck)
data_prep/        build_data.py, build_deck.py, TRANSLATION_BRIEF.md, REPORT_BRIEF.md
.streamlit/config.toml   light theme, navy primary, toolbarMode=minimal
```

### Data files
| File | Content | Built by |
|---|---|---|
| `checklist.json` | 1,002 rows, one per checklist item, in the original language. Fields: country, cluster, site_id, site, business_type, lang, row, id, installation, facility_type, activity, norm, eu_directive, requirement, question, evidence, notes, documents, criticality, status, reason, amara_comments, frequency, missing_document, responsible, **criticality_level** (High/Medium/Low/Not rated), **status_level** (Compliant/Partially compliant/Non-compliant/Not applicable/Not assessed) | `data_prep/build_data.py` |
| `translations_en.json` | `{original string: English}`, 4,443 strings | subagents following `TRANSLATION_BRIEF.md` (chunks of ~30k chars) |
| `header_labels.json` | original-language column headers per site (used for headers in Original mode) | `build_data.py` |
| `deck_results.json` | `site_figures`, `group_figures` (MX services aggregate), `cluster_figures`, `global_high`, `site_gaps`, `cluster_gaps`, `global_gaps`, `exec_summary`, `cluster_meta`. Counts are `[compliant, partial, non-compliant]` per High/Medium/Low | `data_prep/build_deck.py` (figures **transcribed by hand** from deck chart images) |
| `site_reports.json` | per site: report_file, report_language, visit_date, summary_strengths, summary_improvements, key_activities[{activity, regulations[], status, comments[]}], quick_wins, recommendations. Text items are `{"en","orig"}` | subagents following `REPORT_BRIEF.md` (status read from dot colours on rendered pages) |

`build_data.py` has **absolute paths** (`/home/claude/src/...`). Edit `SRC/WORK/AMZ/OUT` before re-running.

---

## 6. Data rules (keep consistent)

- **Column mapping**: headers differ per file and language; `FIELD_RULES` in build_data.py maps them by
  normalised prefix (es/fr/it/pt/en). The header row is found by locating the cell `ID`.
- **Criticality**: Alta/Alto/High/Élevée → High; Media/Medio/Moyenne → Medium; Baja/Bajo/Baixa/Bassa/Faible → Low.
  France office uses the reviewed column **"Niveau de criticité AA"**.
- **Status**: Cumplido/Conforme/Cumple/Fully → Compliant; Parcial…/Parzialmente… → Partially compliant;
  No conforme/non conforme → Non-compliant; **Pendiente/Pending → Non-compliant** (evidence pending);
  No aplica/No relevante/N/A/Não Relevante/Non applicabile → Not applicable; empty → Not assessed.
- **France checklists have no status text**: status is the **cell fill colour** (FF0000 red = non-compliant,
  FFC000 amber = partial).
- Where the reason column is missing, the site's "Comentarios" column is used as the reason.
- Braskem's checklist wrongly says "Almacén Iberdrola" in the Instalación column (source error, left as-is).
- **Deck vs Excel**: deck figures do not always equal checklist counts (e.g. France office deck = 18 items,
  Excel = 30 rows; the Greece & Italy cluster chart is off by 1 vs its site charts). Charts in tabs ②–④ use
  **deck figures**; tables use Excel. Tab ② labels the source under each chart.
- Sites without their own deck chart (MX-IBE, MX-SCH, MX-BRA are reported as one "Mexico services" aggregate;
  MX-CHE and MX-ALT were remote and not charted) → tab ② computes the chart from the checklist and says so.
- Global high-criticality totals must equal the deck: **184 compliant / 72 partial / 89 non-compliant**.

---

## 7. What each tab does now

**Header**: large dss+ logo | eyebrow + title + flags | Amara NZero logo, green gradient rule below.
**Navigation** (v0.2): four equal rectangular boxes filling the row (`st.radio` key `nav`, styled via
`.st-key-navbox`; only the selected page is rendered) and the **Translate** box on the same row at the right
(`st.radio` key `lang_widget` → `st.session_state["lang_mode"]`). Every text value passes through `T()`/`RT()`.
Site selection (`sel_cluster/sel_country/sel_site`) is kept alive across pages by re-assigning those keys at the
top of each run.

**① Legal requirements** (general overview, no company performance and no criticality): title "Identification of key
activities and legal requirements", subtitle "Legal requirements identified for Amara NZero's activities";
KPIs; treemap All countries → country → type of business with the count on every tile (a single root node lets you zoom
back out); country × type count matrix with totals; top-15 referenced regulations; requirements per site coloured
by type; **register** (Country, Site, Type of business, ID, Key activity, Legal requirement, Standard / Reference)
with its own filters (country, site, type, key activity, text search) and Excel/CSV export.
The earlier top filter bar and "Key activities and related regulations" cards were removed at the owner's request.

**② Site compliance**: selectboxes `sel_cluster` → `sel_country` → `sel_site`; site banner; KPIs; deck
criticality chart + key gaps panel; status donut + crosstab; compliance by key activity; site-visit report
table (activity, regulations, coloured dot, comments, filterable by status); strengths / improvements /
quick wins / recommendations; full checklist with criticality/status/search filters, status-coloured cells, export.

**③ Cluster results**: cluster = cluster of `sel_site`; banner (scope, headline); KPIs; business×criticality
multicategory stacked chart + gaps panel; per-site small multiples; compliance mix by type; % compliant heatmap.

**④ Global · high criticality**: KPIs; deck chart (bars per cluster inside business-type groups, SVG flags as
Plotly layout images) + gaps panel; one high-criticality chart per cluster; 100% mix per cluster and per type;
all criticality levels per cluster; executive summary strengths/gaps.

### Style
Navy `#1B1F3B` text and titles; status colours Compliant `#1FA276`, Partial `#F0A02C`, Non-compliant `#E24B47`;
grey panels `#F2F3F5`; Amara green `#009B3A` / lime `#C4D600` rule under the header; dss+ red `#E1261C` accents;
Montserrat (Google Fonts, falls back offline). Stacked bars have a white 1.5px gap and values inside segments.

---

## 8. Gotchas found while building

- `st.tabs` markup differs between Streamlit versions (the owner's install showed unstyled tabs), so navigation
  now uses a styled `st.radio`. Its CSS targets `div[role="radiogroup"] > *` and `:has(input:checked)`, which works
  with both the old (baseweb) and new (react-aria) radio markup.
- Python 3.11: an f-string expression cannot contain a backslash (caused a SyntaxError once).
- `load_all()` must be `st.cache_resource`, **not** `cache_data`: cache_data copies the whole dataset on every
  `T()` call, which made English mode about 10× slower.
- Streamlit's page scroll lives in an inner container; Playwright `full_page` screenshots need a tall viewport.
- `AppTest`: set cascading selectboxes one at a time with `.run()` between them.
- `plotly` bars: set `textangle=0` or thin segments show rotated labels.

## 9. How it was tested
- `streamlit.testing.v1.AppTest` looped over all 23 sites in Original and English: 0 exceptions.
- Playwright screenshots of every tab in both modes, checked visually.
- Global high totals checked against the deck (184/72/89); Spain warehouse cluster sums checked against site charts.

---

## 10. Open items / next steps
- [x] UI round 1: header, 4-box navigation with Translate alongside, page 1 simplified to a general overview.
- [ ] Next UI rounds on pages 2–4 (owner to supply).
- [ ] Decide whether the translate switch should also translate UI labels into the source language (today the
      UI chrome stays English; only data and report text switch).
- [ ] Spot-check translations with native speakers for the sensitive legal terms (see TRANSLATION_BRIEF.md).
- [ ] Confirm with report authors: Portugal "MAP" row and Madrid "Emergency Plan" row show a green dot although
      the comments list gaps (kept as printed).
- [ ] `build_data.py`: replace absolute paths with CLI arguments / relative paths.
- [ ] Optional: add the `01. Identification of legal requirements` PDF (Requisitos legales) content to tab ①.
- [ ] Optional: Bradley Curve / safety-culture section (in the decks but out of scope so far).
- [ ] Make the repo private (client-confidential data).

---

## v0.4 — Translation model and Excel datasets (owner tasks 1–2, Oct 2026)

**Translate dropdown** (`lang_widget`): two options.
- **Original**: everything in the language of the *region in focus*: the country of the site selected in Site
  compliance (pages 2–4 and page 1), or, on page 1, the single country chosen in the register's Country filter.
  Checklist rows and report findings are shown as written in their source documents; every English-authored text
  (interface, deck insights, English report findings, report regulation labels, chart labels) is translated into
  that language from `data/lang/<es|fr|it|pt>.json`. Greece = English (its documents are English).
- **English**: everything in English (`data/translations_en.json` for checklist cells).
- The note under the dropdown shows which language "Original" currently means.
- Filters whose labels change with the language use per-language widget keys (`r_site_<lang>`, `ck_status_<lang>`,
  …) because Streamlit stores multiselect selections as displayed labels. The page-1 country filter uses native
  country names in Original mode (`r_country_Original`).
- `core._MISSES` records every English string requested without a translation. Coverage check: run every site ×
  page × mode with AppTest (fresh app per state) and confirm the only misses are source-language checklist text.
  Result at v0.4: 0 untranslated English strings, 0 exceptions across 23 sites × 4 pages × 2 modes.

**Excel datasets**
- `exports/Amara_NZero_Legal_Compliance_Records.xlsx`: complete, unfiltered records. Page 1 requirements and page 2
  assessed checklist for all countries, clusters and sites combined, plus report key activities and findings, each in
  an Original and an English sheet, with status/criticality mappings and a site list.
- `exports/Amara_NZero_Dashboard_Chart_Data.xlsx`: one sheet per dashboard chart (pages 1–4) with its data table,
  SUM totals and a native Excel chart, plus QA reconciliation sheets.
- Both are built by `exports.py` (also offered as in-app downloads); `python data_prep/export_excel.py` rewrites them.
- `data/site_checklists/<SITE_ID>_<source file>.xlsx`: each working checklist with an identical English copy of
  every sheet ("<sheet> (EN)") right after the original: same layout, merged cells, fills and widths. Greece is
  copied unchanged (already English). Rebuild with
  `python data_prep/build_site_workbooks.py <working-files folder> <Chetumal/Altamira folder>`;
  `_build_report.json` lists any cell left untranslated (only one formula cell).

**Data correction carried in this version**: MX-IBE, MX-BRA and MX-ALT checklists contain continuation rows without
an ID; they are now included (17 → 30 records each; total 1,002 → 1,041). All other sites match their source row
counts (`data/qa_results.json` → reconciliation_summary).

**Page 2 layout**: the assessed checklist table now sits above the site-visit report findings (strengths, areas for
improvement, quick wins, recommendations).

**Next**: task 3: full QA/QC of source Excel ↔ dataset ↔ dashboard tables ↔ deck charts ↔ translations; task 5:
final accuracy pass on site-visit report content.

---

## v0.5 — Translate dropdown lists real languages (Oct 2026)

- The dropdown (box styled like the four section boxes, with arrow) offers the languages of the country / cluster on
  screen plus English: page 2 = the site's language + English (Greece: English only); page 3 = the cluster's
  languages + English (e.g. Spain & Portugal → Español, Português, English); page 1 = languages of the countries in
  the register filter (all four if no filter) + English; page 4 = all languages + English. State: `lang_code`.
  If the chosen language is not offered on the next page, the page's own language is used (English stays English).
- Checklist rows appear as written when their source language is the chosen one; otherwise in English (page 1 with
  mixed countries says so under the register title). English-authored text uses `data/lang/<code>.json`.
- `pandas.Styler` needs `jinja2` (now in requirements.txt); without it the page-2 table falls back to no colours.
- Check: `python data_prep/check_translation_coverage.py` → 117 page/language states, 0 errors, 0 untranslated texts.