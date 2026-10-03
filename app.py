"""Amara NZero — Safety & Legal Compliance Assessment dashboard (dss+, June 2026).

Run:  streamlit run app.py

Language model: every visible text passes through L() (interface / deck text, authored in English), RT() (site-visit
report findings) or T() (checklist cells). Translate dropdown: 'Original' = everything in the language of the region in
focus (checklists/reports as written, English-authored text translated via data/lang/<lang>.json); 'English' =
everything in English.
"""
import io

import pandas as pd
import streamlit as st

import charts as C
from core import (AMARA_GREEN, ASSETS, BUSINESS_ORDER, CLUSTER_ORDER, COUNTRY_CODE, COUNTRY_LANG, COUNTRY_ORDER,
                  CRIT_ORDER, DSS_RED, INK_2, LANG_CHOICES, LANG_NAME, MUTED, NATIVE_COUNTRY_NAME, NATIVE_LANG_NAME, NAVY,
                  PANEL, STATUS_COLORS, STATUS_ORDER, L, RT, T, column_labels, counts_from_checklist, english_of, esc,
                  flag_html, gap_panel_html, img_b64, is_en, kpi_row, lang_choice, load_all, page_languages,
                  section, split_regulations, translate_df, ui_lang)
from exports import build_graph_workbook, build_records_workbook

st.set_page_config(page_title="Amara NZero · Legal Compliance", page_icon="🛡️", layout="wide",
                   initial_sidebar_state="collapsed")

df, TRMAP, DECK, REPORTS, HEADERS, SITES, I18N = load_all()
SITE = SITES.set_index("site_id")

# Resolve the Region → Country → Site cascade *before* anything is drawn, the same way the drop-downs on page 2
# will (an option that is no longer valid falls back to the first one). This keeps the selection alive while other
# pages are shown, and lets the Translate box know the country / cluster on screen in the same run.
_ss = st.session_state
PAGES = ["Legal requirements", "Site compliance", "Cluster results", "Global · high criticality"]
# The page lives in its own state ("page"): the section buttons are translated, and Streamlit would treat translated
# buttons as a new widget and reset them to page 1 whenever the language changes.
if _ss.get("page") not in PAGES:
    _ss["page"] = _ss.get("nav") if _ss.get("nav") in PAGES else PAGES[0]
_ss["nav"] = _ss["page"]
_cl = _ss.get("sel_cluster") if _ss.get("sel_cluster") in CLUSTER_ORDER else CLUSTER_ORDER[0]
_countries = [c for c in COUNTRY_ORDER if c in set(SITES[SITES.cluster == _cl].country)]
_co = _ss.get("sel_country") if _ss.get("sel_country") in _countries else _countries[0]
_sites = list(SITES[SITES.country == _co].site_id)
_ss["sel_cluster"], _ss["sel_country"] = _cl, _co
_ss["sel_site"] = _ss.get("sel_site") if _ss.get("sel_site") in _sites else _sites[0]

# Translate options = languages of the country / cluster on screen + English. English is the default: whenever the
# page or the set of available languages changes, the language goes back to English.
LANG_OPTS = page_languages()
_sig = (_ss["page"], tuple(LANG_OPTS))
if _ss.get("_lang_sig") != _sig or _ss.get("lang_code", "en") not in LANG_OPTS:
    _ss["lang_code"] = "en"
    _ss["_lang_sig"] = _sig

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], .stMarkdown, .stText, button, input, textarea, select {{
  font-family: Montserrat, 'Segoe UI', Helvetica, Arial, sans-serif; }}
.stApp {{ background:#FFFFFF; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px; }}
header[data-testid="stHeader"] {{ background: transparent; height: 0; }}
.topbar {{ display:flex; align-items:center; gap:28px; padding:14px 6px 16px 6px; }}
.topbar img.dss {{ height:72px; }}
.topbar img.amara {{ height:84px; }}
.topbar .divider {{ width:1px; align-self:stretch; background:#DCDFE6; }}
.eyebrow {{ color:{INK_2}; font-size:14px; font-weight:600; letter-spacing:1.2px; text-transform:uppercase; }}
.apptitle {{ color:{NAVY}; font-weight:800; font-size:36px; line-height:1.12; margin:4px 0 6px 0; letter-spacing:-.3px; }}
.subtitle {{ color:{MUTED}; font-size:14px; }}
.flagstrip img {{ height:17px; margin-right:4px; }}
.greenrule {{ height:5px; background:linear-gradient(90deg,{AMARA_GREEN} 0%, #1FA276 55%, #C4D600 100%);
  border-radius:3px; margin:0 0 14px 0; }}
/* navigation: four rectangular boxes filling the row (works with old and new Streamlit radio markup) */
.st-key-navbox, .st-key-navbox [data-testid="stElementContainer"], .st-key-navbox [data-testid="stRadio"] {{ width:100% !important; }}
.st-key-navbox div[role="radiogroup"] {{
  display:flex !important; flex-wrap:nowrap; gap:10px; width:100%; }}
.st-key-navbox div[role="radiogroup"] > * {{
  flex:1 1 0; margin:0 !important; display:flex; }}
.st-key-navbox div[role="radiogroup"] label {{
  width:100%; margin:0 !important; display:flex; align-items:center; justify-content:center; cursor:pointer; }}
/* hide the radio circle, keep the text */
.st-key-navbox div[role="radiogroup"] label div:not([data-testid="stMarkdownContainer"]):not(:has([data-testid="stMarkdownContainer"])):not([data-testid="stMarkdownContainer"] *) {{
  display:none !important; }}
.st-key-navbox div[role="radiogroup"] > * {{ background:{PANEL}; border:1px solid #DCDFE6; border-radius:6px;
  min-height:52px; transition:all .15s ease; }}
.st-key-navbox div[role="radiogroup"] > *:hover {{ border-color:{NAVY}; background:#E9EBF1; }}
.st-key-navbox div[role="radiogroup"] label {{ padding:12px 10px; }}
.st-key-navbox div[role="radiogroup"] p {{ font-weight:700; font-size:15px; color:{INK_2}; margin:0; text-align:center; }}
.st-key-navbox div[role="radiogroup"] > *:has(input:checked) {{ background:{NAVY}; border-color:{NAVY};
  box-shadow:inset 0 -4px 0 {AMARA_GREEN}; }}
.st-key-navbox div[role="radiogroup"] > *:has(input:checked) p {{ color:white; }}
.st-key-langbox {{ background:{PANEL}; border:1px solid #DCDFE6; border-radius:6px; min-height:52px;
  padding:5px 8px; justify-content:center; }}
/* selectbox box + arrow: new (react-aria) and old (baseweb) Streamlit markup */
.st-key-langbox [data-testid="stSelectbox"] div[role="group"], .st-key-langbox [data-baseweb="select"] > div {{
  background:white; border:1px solid #DCDFE6; min-height:40px; border-radius:5px; cursor:pointer; }}
.st-key-langbox [data-testid="stSelectbox"] input, .st-key-langbox [data-baseweb="select"] div {{
  font-weight:700; color:{NAVY}; font-size:14.5px; cursor:pointer; }}
.st-key-langbox [data-testid="stSelectbox"] svg, .st-key-langbox [data-baseweb="select"] svg {{
  color:{NAVY}; fill:{NAVY}; opacity:1; width:22px; height:22px; }}
.navrule {{ height:2px; background:#E6E8EE; margin:6px 0 4px 0; }}
/* sections, kpis */
.section h3 {{ color:{NAVY}; font-weight:800; font-size:22px; margin:18px 0 2px 0; }}
.section p {{ color:{INK_2}; font-size:14px; margin:0 0 10px 0; }}
.kpi-row {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin:6px 0 10px 0; }}
.kpi {{ background:{PANEL}; border-radius:10px; padding:12px 14px; border-left:4px solid {NAVY}; }}
.kpi-label {{ color:{INK_2}; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.4px; }}
.kpi-value {{ font-size:28px; font-weight:800; line-height:1.2; }}
.kpi-sub {{ color:{MUTED}; font-size:12px; }}
.gap-panel {{ background:{PANEL}; border-radius:10px; padding:14px 18px; font-size:13px; color:{NAVY};
  max-height:520px; overflow-y:auto; }}
.gap-title {{ font-weight:800; text-decoration:underline; margin-bottom:6px; font-size:14px; }}
.gap-h {{ font-weight:700; margin:10px 0 2px 0; }}
.gap-panel ul {{ margin:0 0 4px 0; padding-left:18px; }} .gap-panel li {{ margin:3px 0; }}
.gap-panel ul.sub {{ list-style:square; margin-top:2px; }} .gap-panel p {{ margin:2px 0 6px 0; }}
.gap-sub {{ font-weight:700; margin:4px 0 0 0; }} .gap-panel .mark {{ font-weight:700; color:{DSS_RED}; }}
.gap-foot {{ color:{MUTED}; font-size:11.5px; margin-top:8px; font-style:italic; }}
.st-key-dlbox {{ background:{PANEL}; border:1px solid #DCDFE6; border-radius:10px; padding:12px 16px 4px 16px; margin-top:26px; }}
.dltitle {{ font-weight:800; color:{NAVY}; font-size:15px; }} .dlsub {{ color:{INK_2}; font-size:12.5px; margin-bottom:6px; }}
.pill {{ display:inline-flex; align-items:center; gap:6px; border-radius:999px; padding:2px 10px; font-size:12px;
  font-weight:600; white-space:nowrap; }}
.pill i {{ width:9px; height:9px; border-radius:50%; display:inline-block; }}
.card {{ background:white; border:1px solid #E6E8EE; border-radius:10px; padding:12px 14px; height:100%; }}
.card h4 {{ margin:0 0 6px 0; font-size:14px; color:{NAVY}; font-weight:700; }}
.card ul {{ margin:0; padding-left:16px; font-size:12.5px; color:{INK_2}; }}
table.assess {{ width:100%; border-collapse:collapse; font-size:13px; }}
table.assess th {{ background:{NAVY}; color:white; text-align:left; padding:9px 10px; position:sticky; top:0; z-index:1; }}
table.assess td {{ border-bottom:1px solid #E6E8EE; padding:10px; vertical-align:top; color:{NAVY}; }}
table.assess tr:nth-child(even) td {{ background:#F7F8FA; }}
table.assess td.act {{ width:26%; border-left:4px solid #F0A02C; }}
table.assess td.act b {{ font-size:13.5px; }}
table.assess td.act ul {{ margin:6px 0 0 0; padding-left:16px; color:{MUTED}; font-size:12px; }}
table.assess td.st {{ width:15%; text-align:center; }}
table.assess td ul {{ margin:0; padding-left:18px; }}
.dot {{ display:inline-block; width:18px; height:18px; border-radius:50%; }}
.scrollbox {{ max-height:620px; overflow-y:auto; border:1px solid #E6E8EE; border-radius:10px; }}
.sitebanner {{ background:{NAVY}; color:white; border-radius:12px; padding:16px 20px; display:flex;
  justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; }}
.sitebanner .t {{ font-size:22px; font-weight:800; }}
.sitebanner .m {{ font-size:13px; opacity:.85; }}
.chip {{ background:rgba(255,255,255,.12); border-radius:999px; padding:4px 12px; font-size:12px; margin-left:6px; }}
.note {{ color:{MUTED}; font-size:12px; }}
.srcnote {{ color:{MUTED}; font-size:11.5px; margin-top:-6px; }}
.footer {{ color:{MUTED}; font-size:11.5px; border-top:1px solid #E6E8EE; margin-top:28px; padding-top:10px;
  display:flex; justify-content:space-between; }}
div[data-testid="stDataFrame"] {{ border:1px solid #D5D8E0; border-radius:8px; }}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────────
flags = "".join(flag_html(c, 17) for c in ["ES", "PT", "MX", "CO", "FR", "GR", "IT"])
st.markdown(f"""
<div class="topbar">
  <img class="dss" src="data:image/png;base64,{img_b64(ASSETS / 'dss_logo.png')}" alt="dss+">
  <div class="divider"></div>
  <div style="flex:1">
    <div class="eyebrow">{esc(L("Safety, Legal Compliance & Culture Assessment · 2026"))}</div>
    <div class="apptitle">{esc(L("Legal & Regulatory Compliance — Amara NZero"))}</div>
    <div class="subtitle"><span class="flagstrip">{flags}</span>&nbsp; {esc(L("7 countries · 4 clusters · 23 sites assessed"))}</div>
  </div>
  <img class="amara" src="data:image/png;base64,{img_b64(ASSETS / 'amara_logo.png')}" alt="Amara NZero">
</div>
<div class="greenrule"></div>""", unsafe_allow_html=True)

# ── Navigation (four boxes) + translate dropdown on the same row ─────────────────
nav_col, lang_col = st.columns([5, 1.25], vertical_alignment="center", gap="medium")
with nav_col:
    with st.container(key="navbox"):
        def _set_page():
            st.session_state["page"] = st.session_state["nav"]

        PAGE = st.radio("Section", PAGES, horizontal=True, key="nav", label_visibility="collapsed", format_func=L,
                        on_change=_set_page)
with lang_col:
    with st.container(key="langbox"):
        _lang_key = "lang_sel_" + "_".join(LANG_OPTS)
        st.session_state[_lang_key] = st.session_state["lang_code"]

        def _set_lang(k=_lang_key):
            st.session_state["lang_code"] = st.session_state[k]

        st.selectbox(L("Translate"), LANG_OPTS, key=_lang_key, on_change=_set_lang, label_visibility="collapsed",
                     format_func=lambda c: "🌐  " + NATIVE_LANG_NAME[c])
st.markdown('<div class="navrule"></div>', unsafe_allow_html=True)


def to_excel(frame, sheet="Data"):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        frame.to_excel(xw, index=False, sheet_name=sheet[:31])
        ws = xw.sheets[sheet[:31]]
        for i, col in enumerate(frame.columns, 1):
            ws.column_dimensions[ws.cell(1, i).column_letter].width = min(60, max(12, len(str(col)) + 2))
        ws.freeze_panes = "A2"
    return buf.getvalue()


@st.cache_data(show_spinner=False)
def records_xlsx():
    return build_records_workbook()


@st.cache_data(show_spinner=False)
def graphs_xlsx():
    return build_graph_workbook()


XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
REP_NOTE = ("Where several sites share a requirement, the wording and references shown are those of the first site "
            "listed; each site's own wording is in Site compliance and in the Excel records.")
UNIQUE_NOTE = ("A requirement that applies to several sites, or to several types of business in a country, is counted once "
               "in the country total; the same obligation adapted to each region (city, regional law or authority) counts "
               "once.")
COUNT_RULES = [
    "One unique legal requirement = one legal obligation within a country.",
    "The same obligation at several sites counts once, even when each site's checklist adapts it to its region "
    "(city, regional law, regional authority) and numbers it differently.",
    "Rows repeated inside one checklist (e.g. one line per piece of evidence) count once.",
    "A requirement shared by two types of business in a country (e.g. the Vitoria factory and the warehouses) counts "
    "once in the country total.",
    "Compliance results are still assessed per site and per checklist row in Site compliance.",
]
NO_COMMENTS = f'<li style="list-style:none;color:#8A8FA3">{esc(L("No comments recorded"))}</li>'


def lang_badge(langs):
    langs, lc = set(langs), lang_choice()
    if langs == {lc}:
        return L("Showing original language") + " · " + NATIVE_LANG_NAME[lc]
    if lc == "en":
        return L("Showing English translation")
    return L("Rows written in {lang} are shown as written; rows from other countries are shown in English.").format(
        lang=NATIVE_LANG_NAME[lc])


def card(title, items, color, allow_br=False):
    lis = "".join(f"<li>{esc(x).replace(chr(10), '<br>') if allow_br else esc(x)}</li>" for x in items) or "<li>—</li>"
    return f'<div class="card" style="border-top:4px solid {color}"><h4>{esc(title)}</h4><ul>{lis}</ul></div>'


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Identification of legal requirements (general overview, no company performance)
# ══════════════════════════════════════════════════════════════════════════════
if PAGE == PAGES[0]:
    section(esc(L("Identification of key activities and legal requirements")),
            esc(L("Legal requirements identified for Amara NZero's activities")))

    view = df.copy()
    view["site_order"] = view.site_id.map({s: k for k, s in enumerate(SITES.site_id)})
    regs = view.norm.map(split_regulations).explode().dropna()
    by_type, by_country, n_unique = C.unique_counts(view)
    kpi_row([
        (L("Legal requirements"), f"{n_unique:,}",
         L("unique, from {rows} checklist rows").format(rows=f"{len(view):,}")),
        (L("Key activities"), f"{view.activity.nunique():,}", L("activity groups")),
        (L("Regulations referenced"), f"{regs.nunique():,}", L("laws, decrees, standards")),
        (L("Sites"), f"{view.site_id.nunique()}", L("{n} countries").format(n=view.country.nunique())),
        (L("Types of business"), f"{view.business_type.nunique()}",
         " · ".join(L(b) for b in BUSINESS_ORDER if b in set(view.business_type))),
    ])

    st.markdown(f"**{L('Requirements by country and type of business')}** · "
                f"{L('number of unique legal requirements (click a country to focus, click the top bar to go back)')}")
    st.plotly_chart(C.treemap(view, height=470), width="stretch", config=C.CONFIG, key="t1_tree")
    st.markdown(f'<div class="srcnote">{esc(L(UNIQUE_NOTE))}</div>', unsafe_allow_html=True)

    # ── Register: one row per unique legal requirement per country ───────────────
    section(esc(L("Legal requirements register")),
            esc(lang_badge(view.lang)) + " · " + esc(L("one row per unique legal requirement · filter by country, site, "
                                                        "type of business, key activity or requirement")))
    rep = (view.sort_values(["site_order", "row"]).groupby("req_uid", sort=False)
               .agg(country=("country", "first"), lang=("lang", "first"), activity=("activity", "first"),
                    requirement=("requirement", "first"), norm=("norm", "first"),
                    types=("business_type", lambda s: [b for b in BUSINESS_ORDER if b in set(s)]),
                    site_ids=("site_id", lambda s: list(dict.fromkeys(s))),
                    source_ids=("id", lambda s: list(dict.fromkeys(x for x in s if x))))
               .reset_index())
    rep["activity_disp"] = rep.activity.map(T)
    f1, f2, f3, f4, f5 = st.columns([1, 1.3, 1, 1.5, 1.5])
    with f1:
        r_country = st.multiselect(L("Country"), COUNTRY_ORDER, placeholder=L("All countries"), key="r_country",
                                   format_func=lambda c: NATIVE_COUNTRY_NAME[c])
    reg = rep if not r_country else rep[rep.country.isin(r_country)]
    with f2:
        site_opts = [s for s in SITES.site_id if s in {x for l in reg.site_ids for x in l}]
        r_site = st.multiselect(L("Site"), site_opts, placeholder=L("All sites"), key=f"r_site_{ui_lang()}",
                                format_func=lambda s: L(SITE.site[s]))
    reg = reg if not r_site else reg[reg.site_ids.map(lambda l: bool(set(l) & set(r_site)))]
    with f3:
        r_type = st.multiselect(L("Type of business"), [b for b in BUSINESS_ORDER if b in {x for l in reg.types for x in l}],
                                placeholder=L("All types"), key=f"r_type_{ui_lang()}", format_func=L)
    reg = reg if not r_type else reg[reg.types.map(lambda l: bool(set(l) & set(r_type)))]
    with f4:
        r_act = st.multiselect(L("Key activity"), sorted(set(reg.activity_disp)), placeholder=L("All activities"),
                               key=f"r_act_{ui_lang()}")
    reg = reg if not r_act else reg[reg.activity_disp.isin(r_act)]
    with f5:
        r_q = st.text_input(L("Requirement / regulation contains"), placeholder=L("e.g. ATEX, RD 486/1997, contractor…"),
                            key="r_q")
    if r_q:
        q = r_q.lower()
        mask = pd.Series(False, index=reg.index)
        for c in ["requirement", "norm", "activity"]:
            mask |= reg[c].str.lower().str.contains(q, regex=False)
            mask |= reg[c].map(english_of).str.lower().str.contains(q, regex=False)
        reg = reg[mask]

    out = pd.DataFrame({
        "country": reg.country.map(L),
        "business_type": reg.types.map(lambda l: ", ".join(L(b) for b in l)),
        "site": reg.site_ids.map(lambda l: ", ".join(L(SITE.site[s]) for s in l)),
        "req_uid": reg.req_uid,
        "activity": [T(v, s) for v, s in zip(reg.activity, reg.lang)],
        "requirement": [T(v, s) for v, s in zip(reg.requirement, reg.lang)],
        "norm": [T(v, s) for v, s in zip(reg.norm, reg.lang)],
        "source_ids": reg.source_ids.map(", ".join),
    })
    labels = {**column_labels(["country", "business_type", "activity", "requirement", "norm"]),
              "site": L("Sites"), "req_uid": L("Requirement ID"), "source_ids": L("Checklist IDs")}
    out = out.rename(columns=labels)
    st.dataframe(out, hide_index=True, height=600, width="stretch", row_height=40,
                 column_config={labels["country"]: st.column_config.TextColumn(labels["country"], width="small"),
                                labels["business_type"]: st.column_config.TextColumn(labels["business_type"], width="small"),
                                labels["site"]: st.column_config.TextColumn(labels["site"], width="medium"),
                                labels["req_uid"]: st.column_config.TextColumn(labels["req_uid"], width="small"),
                                labels["activity"]: st.column_config.TextColumn(labels["activity"], width="medium"),
                                labels["requirement"]: st.column_config.TextColumn(labels["requirement"], width="large"),
                                labels["norm"]: st.column_config.TextColumn(labels["norm"], width="large"),
                                labels["source_ids"]: st.column_config.TextColumn(labels["source_ids"], width="small")})
    d0, d1, d2 = st.columns([4, 1, 1])
    d0.markdown(f'<div class="note">{esc(L("{n} of {total} unique legal requirements shown.").format(n=f"{len(out):,}", total=f"{n_unique:,}"))} '
                f'{esc(L(REP_NOTE))}</div>',
                unsafe_allow_html=True)
    d1.download_button("⬇ Excel", to_excel(out, "Legal requirements"), "amara_legal_requirements_filtered.xlsx", XLSX,
                       width="stretch")
    d2.download_button("⬇ CSV", out.to_csv(index=False).encode("utf-8-sig"), "amara_legal_requirements_filtered.csv",
                       "text/csv", width="stretch")

    # ── Unique requirements per site ──────────────────────────────────────────────
    st.write("")
    c3, c4 = st.columns([1.35, 1], gap="large")
    with c3:
        st.markdown(f"**{L('Requirements per site')}** · {L('unique legal requirements, coloured by type of business')}")
        st.plotly_chart(C.site_bars(view, height=560), width="stretch", config=C.CONFIG, key="t1_sites")
    with c4:
        st.markdown(f"**{L('How requirements are counted')}**")
        st.markdown(f'<div class="card"><ul>'
                    + "".join(f"<li>{esc(L(x))}</li>" for x in COUNT_RULES) + "</ul></div>", unsafe_allow_html=True)
        st.write("")
        stab = C.site_table(view)
        dup = stab[stab.rows != stab.n]
        if len(dup):
            st.markdown(f'<div class="note">{esc(L("Sites whose checklist repeats a requirement on several rows"))}</div>',
                        unsafe_allow_html=True)
            st.dataframe(pd.DataFrame({L("Site"): dup.site.map(L), L("Checklist rows"): dup.rows,
                                       L("Unique legal requirements"): dup.n}), hide_index=True, width="stretch")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Site drill-down
# ══════════════════════════════════════════════════════════════════════════════
if PAGE == PAGES[1]:
    section(esc(L("Legal compliance assessment by site")),
            esc(L("Choose a region, country and site to see its compliance results, key gaps, the site-visit findings "
                  "and the full assessed checklist.")))
    s1, s2, s3 = st.columns([1, 1, 1.6])
    with s1:
        sel_cluster = st.selectbox(L("Region (cluster)"), CLUSTER_ORDER, key="sel_cluster", format_func=L)
    with s2:
        countries = [c for c in COUNTRY_ORDER if c in set(SITES[SITES.cluster == sel_cluster].country)]
        sel_country = st.selectbox(
            L("Country"), countries, key="sel_country",
            format_func=lambda c: f"{L(c)}  ({(SITES.country == c).sum()} {L('site') if (SITES.country == c).sum() == 1 else L('sites')})")
    with s3:
        site_opts = SITES[SITES.country == sel_country]
        sel_site = st.selectbox(L("Site"), list(site_opts.site_id), key="sel_site",
                                format_func=lambda s: f"{L(SITE.site[s])} · {L(SITE.business_type[s])}")

    srow = SITE.loc[sel_site]
    sdf = df[df.site_id == sel_site].copy()
    rep = REPORTS.get(sel_site, {})
    rlang = rep.get("report_language", "en")
    visit = rep.get("visit_date", "")
    st.markdown(f"""<div class="sitebanner"><div>
        <div class="t">{flag_html(COUNTRY_CODE[srow.country], 20)} {esc(L(srow.site))}</div>
        <div class="m">{esc(L(srow.country))} · {esc(L(srow.cluster))} · {esc(L("Type of business"))}: <b>{esc(L(srow.business_type))}</b>
        {' · ' + esc(L("Visit")) + ': ' + esc(L(visit)) if visit else ''}</div></div>
        <div><span class="chip">{esc(L("Checklist language"))}: {esc(L(LANG_NAME.get(srow.lang, srow.lang)))}</span>
        <span class="chip">{esc(L("{n} requirements assessed").format(n=len(sdf)))}</span></div></div>""",
                unsafe_allow_html=True)

    sc = sdf.status_level.value_counts()
    assessed = int(sum(sc.get(k, 0) for k in STATUS_ORDER))
    hi_gap = int(((sdf.criticality_level == "High") & sdf.status_level.isin(["Non-compliant", "Partially compliant"])).sum())
    pct = lambda k: L("{p}% of assessed").format(p=f"{sc.get(k, 0) / assessed * 100:.0f}") if assessed else ""
    pend = sdf.status.str.lower().str.startswith(("pend",)).any()
    kpi_row([
        (L("Requirements"), f"{len(sdf)}", L("{n} with a compliance result").format(n=assessed)),
        (L("Compliant"), f"{sc.get('Compliant', 0)}", pct("Compliant"), STATUS_COLORS["Compliant"]),
        (L("Partially compliant"), f"{sc.get('Partially compliant', 0)}", pct("Partially compliant"), "#D9822B"),
        (L("Non-compliant"), f"{sc.get('Non-compliant', 0)}",
         pct("Non-compliant") + (" · " + L("incl. pending evidence") if pend else ""), STATUS_COLORS["Non-compliant"]),
        (L("High-criticality gaps"), f"{hi_gap}", L("high criticality, not fully compliant"), DSS_RED),
    ])

    # Row 1: official chart + key gaps panel
    g1, g2 = st.columns([1.05, 1])
    with g1:
        st.markdown(f"**{L('Compliance status by criticality')}**")
        if sel_site in DECK["site_figures"]:
            figd = DECK["site_figures"][sel_site]
            src = esc(L("Source: figures as reported in the dss+ cluster presentation (June 2026)."))
        else:
            figd = counts_from_checklist(sdf)
            src = esc(L("Source: calculated from the site checklist (this site has no separate chart in the cluster deck)."))
            grp = DECK["group_figures"]["MX-SERVICES"]
            if sel_site in grp["sites"]:
                h = grp["figures"]
                src += " " + esc(L("The deck reports Mexico in-house services (Iberdrola, Schneider, Braskem) together: "
                                   "High {h}, Medium {m}, Low {l} (compliant / partial / non-compliant) — see Cluster results.")
                                 .format(h="/".join(map(str, h["High"])), m="/".join(map(str, h["Medium"])),
                                         l="/".join(map(str, h["Low"]))))
        st.plotly_chart(C.criticality_stack(figd, height=380), width="stretch", config=C.CONFIG, key="site_crit")
        st.markdown(f'<div class="srcnote">{src}</div>', unsafe_allow_html=True)
    with g2:
        gaps = DECK["site_gaps"].get(sel_site)
        if gaps:
            st.markdown(gap_panel_html(gaps["panel_title"], gaps["groups"], gaps.get("footnote", "")),
                        unsafe_allow_html=True)
            st.markdown(f'<div class="srcnote" style="margin-top:6px">{esc(L("Source"))}: {esc(L(gaps["source"]))}</div>',
                        unsafe_allow_html=True)
        else:
            hi = sdf[(sdf.criticality_level == "High") & (sdf.status_level == "Non-compliant")]
            items = [{"text": f"{T(a)}: {T(r)}", "mark": "", "sub": []} for a, r in zip(hi.activity, hi.reason)]
            st.markdown(gap_panel_html("Key compliance gaps (high criticality, from checklist)",
                                       [{"heading": "High criticality – not compliant", "bullets": items[:12]}]),
                        unsafe_allow_html=True)
            st.markdown(f'<div class="srcnote" style="margin-top:6px">'
                        f'{esc(L("This site has no key-gaps panel in the cluster deck; items listed from its checklist."))}'
                        f'</div>', unsafe_allow_html=True)

    # Row 2: status donut + activity hotspot
    a1, a2 = st.columns([0.8, 1.4])
    with a1:
        st.markdown(f"**{L('Overall status of all checklist items')}**")
        st.plotly_chart(C.status_donut(sc.to_dict(), height=330), width="stretch", config=C.CONFIG, key="site_donut")
        crit_tab = (sdf.pivot_table(index="criticality_level", columns="status_level", values="id", aggfunc="count", fill_value=0)
                       .reindex([c for c in CRIT_ORDER + ["Not rated"] if c in set(sdf.criticality_level)]))
        crit_tab = crit_tab[[c for c in STATUS_ORDER + ["Not applicable", "Not assessed"] if c in crit_tab.columns]]
        crit_tab.index = [L(i) for i in crit_tab.index]
        crit_tab.columns = [L(c) for c in crit_tab.columns]
        st.markdown(f'<div class="note">{esc(L("Checklist records by criticality and status"))}</div>', unsafe_allow_html=True)
        st.dataframe(crit_tab.rename_axis(L("Criticality")), width="stretch")
    with a2:
        st.markdown(f"**{L('Compliance by key activity')}** · {L('where the gaps concentrate (checklist)')}")
        act = (sdf[sdf.status_level.isin(STATUS_ORDER)]
               .assign(act=lambda d: d.activity.map(T).str.slice(0, 55))
               .pivot_table(index="act", columns="status_level", values="id", aggfunc="count", fill_value=0))
        for s in STATUS_ORDER:
            if s not in act.columns:
                act[s] = 0
        act = act[STATUS_ORDER].sort_values(["Non-compliant", "Partially compliant"], ascending=False)
        if act.empty:
            st.info(L("No assessed items with a compliance result."))
        else:
            st.plotly_chart(C.activity_bars(act, height=max(330, 70 + 26 * len(act))), width="stretch",
                            config=C.CONFIG, key="site_act")

    # Row 3: site-visit report — key activities assessment
    if rep:
        section(esc(L("Legal compliance assessment · site-visit report")),
                esc(L("Key activities, governing regulations, compliance indicator and findings — from")) +
                f" <i>{esc(rep.get('report_file', ''))}</i>.")
        stf = st.multiselect(L("Show status"), ["Compliant", "Partially compliant", "Non-compliant", "Not assessed"],
                             default=["Compliant", "Partially compliant", "Non-compliant", "Not assessed"], key=f"rep_status_{ui_lang()}",
                             format_func=L)
        rows_html = ""
        for ka in rep.get("key_activities", []):
            if ka.get("status") not in stf:
                continue
            col = STATUS_COLORS.get(ka.get("status"), "#D9DCE2")
            regs_html = "".join(f"<li>{esc(L(r) if rlang == 'en' else r)}</li>" for r in ka.get("regulations", []))
            com = "".join(f'<li style="margin:2px 0">{esc(RT(c, rlang, srow.lang))}</li>'.replace("\n", "<br>")
                          for c in ka.get("comments", [])) or NO_COMMENTS
            rows_html += (f'<tr><td class="act" style="border-left-color:{col}"><b>{esc(RT(ka["activity"], rlang, srow.lang))}</b>'
                          f'<ul>{regs_html}</ul></td>'
                          f'<td class="st"><span class="dot" style="background:{col}"></span><br>'
                          f'<span style="font-size:11.5px;color:{MUTED}">{esc(L(ka.get("status")))}</span></td>'
                          f'<td><ul>{com}</ul></td></tr>')
        st.markdown(f'<div class="scrollbox"><table class="assess"><thead><tr><th>{esc(L("Key activity & regulations"))}</th>'
                    f'<th style="text-align:center">{esc(L("Compliance"))}</th><th>{esc(L("Comments / missing evidence"))}</th>'
                    f'</tr></thead><tbody>{rows_html}</tbody></table></div>', unsafe_allow_html=True)

    # Row 4: full checklist, Excel-style (above the report findings)
    section(esc(L("Assessed checklist · all records for this site")), esc(lang_badge([srow.lang])))
    k1, k2, k3 = st.columns([1, 1.3, 2])
    with k1:
        fc = st.multiselect(L("Criticality"), [c for c in CRIT_ORDER + ["Not rated"] if c in set(sdf.criticality_level)],
                            key=f"ck_crit_{ui_lang()}", placeholder=L("All"), format_func=L)
    with k2:
        fs = st.multiselect(L("Compliance status"), [s for s in STATUS_ORDER + ["Not applicable", "Not assessed"]
                                                      if s in set(sdf.status_level)], key=f"ck_status_{ui_lang()}",
                            placeholder=L("All"), format_func=L)
    with k3:
        fq = st.text_input(L("Search in this checklist"), key="ck_q", placeholder=L("keyword…"))
    cdf = sdf
    if fc:
        cdf = cdf[cdf.criticality_level.isin(fc)]
    if fs:
        cdf = cdf[cdf.status_level.isin(fs)]
    if fq:
        m = pd.Series(False, index=cdf.index)
        for c in ["activity", "norm", "requirement", "question", "evidence", "reason", "notes"]:
            m |= (cdf[c].str.lower().str.contains(fq.lower(), regex=False)
                  | cdf[c].map(english_of).str.lower().str.contains(fq.lower(), regex=False))
        cdf = cdf[m]
    fields = ["id", "activity", "norm", "eu_directive", "requirement", "question", "evidence", "notes", "documents",
              "criticality", "status", "status_level", "reason", "amara_comments", "missing_document", "responsible",
              "frequency"]
    fields = [f for f in fields if (sdf[f] != "").any()]
    out = translate_df(cdf[fields], [f for f in fields if f not in ("id", "status_level")])
    out["status_level"] = cdf.status_level.map(L).values
    labels = column_labels(fields)
    out = out.rename(columns=labels)
    stat_col = labels["status_level"]
    color_by_label = {L(k): v for k, v in STATUS_COLORS.items()}

    def _color_status(v):
        c = color_by_label.get(v)
        return f"background-color:{c}33; color:{NAVY}; font-weight:600" if c else ""

    try:  # pandas Styler needs jinja2; without it the table is shown without status colours
        styled = out.style.map(_color_status, subset=[stat_col])
    except (AttributeError, ImportError):
        styled = out
    wide = {labels[f]: st.column_config.TextColumn(labels[f], width="large") for f in
            ["requirement", "question", "evidence", "reason", "notes", "norm", "amara_comments", "documents"] if f in labels}
    st.dataframe(styled, hide_index=True, height=520, width="stretch", row_height=38,
                 column_config={**wide, labels["id"]: st.column_config.TextColumn(labels["id"], width="small")})
    note = L("{n} of {total} records.").format(n=len(out), total=len(sdf)) + " " + L(
        "'Status (normalised)' maps each recorded status to Compliant / Partially compliant / Non-compliant "
        "(incl. pending evidence) / Not applicable.")
    if (sdf.status_source == "cell colour").any():
        note += " " + L("Where the status cell is empty, the status was read from the cell colour of the checklist.")
    st.markdown(f'<div class="srcnote">{esc(note)}</div>', unsafe_allow_html=True)
    d1, d2, _ = st.columns([1, 1, 4])
    d1.download_button("⬇ Excel", to_excel(out, sel_site), f"amara_{sel_site}_checklist.xlsx", XLSX, width="stretch",
                       key="dl_site_x")
    d2.download_button("⬇ CSV", out.to_csv(index=False).encode("utf-8-sig"), f"amara_{sel_site}_checklist.csv", "text/csv",
                       width="stretch", key="dl_site_c")

    # Row 5: site-visit report findings
    if rep:
        section(esc(L("Site-visit report findings")), "")
        e1, e2 = st.columns(2)
        with e1:
            st.markdown(card("✓ " + L("Strengths"), [RT(x, rlang, srow.lang) for x in rep.get("summary_strengths", [])],
                             STATUS_COLORS["Compliant"]), unsafe_allow_html=True)
        with e2:
            st.markdown(card("✗ " + L("Areas for improvement"), [RT(x, rlang, srow.lang) for x in rep.get("summary_improvements", [])],
                             STATUS_COLORS["Non-compliant"]), unsafe_allow_html=True)
        qw, rc = rep.get("quick_wins", []), rep.get("recommendations", [])
        if qw or rc:
            st.write("")
            q1, q2 = st.columns(2)
            with q1:
                st.markdown(card("⚡ " + L("Quick wins"), [RT(x, rlang, srow.lang) for x in qw], AMARA_GREEN, allow_br=True),
                            unsafe_allow_html=True)
            with q2:
                st.markdown(card("➜ " + L("Recommendations"), [RT(x, rlang, srow.lang) for x in rc], NAVY, allow_br=True),
                            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Cluster of the selected site
# ══════════════════════════════════════════════════════════════════════════════
if PAGE == PAGES[2]:
    cur_site = st.session_state.get("sel_site", SITES.site_id.iloc[0])
    cl = SITE.cluster[cur_site]
    meta = DECK["cluster_meta"][cl]
    summ = DECK["cluster_summary"][cl]
    cfig = DECK["cluster_figures"][cl]
    section(esc(L("{cluster} cluster results").format(cluster=L(cl))),
            esc(L("Cluster of the site selected in Site compliance ({site}). Change the site there to switch cluster. "
                  "Figures as presented in the dss+ cluster results.").format(site=L(SITE.site[cur_site]))))
    intro = "".join(f"<li>{esc(L(x))}</li>" for x in summ.get("intro", []))
    st.markdown(f"""<div class="sitebanner"><div style="max-width:52%"><div class="t">{''.join(flag_html(f, 22) for f in meta['flags'])} {esc(L(cl))}</div>
        <div class="m" style="margin-top:4px">{esc(L(summ['title']))}</div></div>
        <div class="m" style="max-width:46%"><ul style="margin:0;padding-left:16px">{intro}</ul></div></div>""",
                unsafe_allow_html=True)

    tot = [sum(cfig[b][c][i] for b in cfig for c in CRIT_ORDER) for i in range(3)]
    hi = [sum(cfig[b]["High"][i] for b in cfig) for i in range(3)]
    kpi_row([
        (L("Requirements assessed"), f"{sum(tot)}", L("{n} types of business").format(n=len(cfig))),
        (L("Compliant"), f"{tot[0]}", L("{p}% of assessed").format(p=f"{tot[0] / max(1, sum(tot)) * 100:.0f}"),
         STATUS_COLORS["Compliant"]),
        (L("High criticality · non-compliant"), f"{hi[2]}", L("full non-compliance"), STATUS_COLORS["Non-compliant"]),
        (L("High criticality · partial"), f"{hi[1]}", L("limited or incomplete evidence"), "#D9822B"),
        (L("High criticality · compliant"), f"{hi[0]}",
         L("{p}% of high items").format(p=f"{hi[0] / max(1, sum(hi)) * 100:.0f}"), STATUS_COLORS["Compliant"]),
    ])

    m1, m2 = st.columns([1.55, 1])
    with m1:
        st.markdown(f"**{L('Compliance status per criticality of business in the {cluster} cluster').format(cluster=L(cl))}**")
        st.plotly_chart(C.cluster_business_stack(cfig, height=470), width="stretch", config=C.CONFIG, key="cl_main")
    with m2:
        st.markdown(gap_panel_html("High Critical Compliance gaps", DECK["cluster_gaps"][cl]["groups"]),
                    unsafe_allow_html=True)

    csites = SITES[SITES.cluster == cl]
    items, used_group = [], False
    for sid in csites.site_id:
        if sid in DECK["site_figures"]:
            items.append((L(SITE.site[sid]), DECK["site_figures"][sid]))
        elif sid in DECK["group_figures"]["MX-SERVICES"]["sites"] and not used_group:
            used_group = True
            items.append((L("Mexico in-house services") + "*", DECK["group_figures"]["MX-SERVICES"]["figures"]))
    if items:
        section(esc(L("Compliance status by criticality · per site")),
                esc(L("One panel per assessed site, as in the cluster presentation.")))
        st.plotly_chart(C.small_multiples(items, cols=min(5, len(items)), height_per_row=260), width="stretch",
                        config=C.CONFIG, key="cl_sm")
        if used_group:
            st.markdown(f'<div class="srcnote">{esc(L("* Iberdrola, Schneider and Braskem are reported together in the deck. Chetumal and Altamira were assessed remotely and are not charted in the deck (see Site compliance)."))}</div>',
                        unsafe_allow_html=True)

    b1, b2 = st.columns([1, 1.1])
    with b1:
        st.markdown(f"**{L('Compliance mix by type of business')}** ({L('all criticality levels')})")
        types = [b for b in BUSINESS_ORDER if b in cfig]
        data = [[sum(cfig[b][c][i] for c in CRIT_ORDER) for i in range(3)] for b in types]
        st.plotly_chart(C.share_bars([L(t) for t in types], data), width="stretch", config=C.CONFIG, key="cl_share")
    with b2:
        st.markdown(f"**{L('Share compliant by site and criticality')}** — {L('red cells are the priority areas')}")
        rows, z, txt = [], [], []
        for t, d in items:
            rows.append(t)
            zz, tt = [], []
            for c in CRIT_ORDER:
                n = sum(d[c])
                zz.append(d[c][0] / n * 100 if n else None)
                tt.append(f"{d[c][0]}/{n}" if n else "–")
            z.append(zz); txt.append(tt)
        if rows:
            st.plotly_chart(C.heat_rate(rows, z, txt, height=90 + 34 * len(rows)), width="stretch",
                            config=C.CONFIG, key="cl_heat")

    section(esc(L("Cluster summary")), esc(L("From the cluster presentation.")))
    e1, e2 = st.columns(2)
    with e1:
        st.markdown(card("✓ " + L(summ.get("strengths_heading") or "Strengths"), [L(x) for x in summ.get("strengths", [])],
                         STATUS_COLORS["Compliant"]), unsafe_allow_html=True)
    with e2:
        st.markdown(card("✗ " + L(summ.get("gaps_heading") or "Key gaps"), [L(x) for x in summ.get("gaps", [])],
                         STATUS_COLORS["Non-compliant"]), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Global, highest criticality
# ══════════════════════════════════════════════════════════════════════════════
if PAGE == PAGES[3]:
    section(esc(L("Global results · high criticality")),
            esc(L("High-criticality legal requirements across all clusters by type of business, as presented in the "
                  "Global Results Presentation (June 2026).")))
    gh = DECK["global_high"]
    tot = [sum(r["values"][i] for r in gh) for i in range(3)]
    kpi_row([
        (L("High-criticality items"), f"{sum(tot)}", L("across 4 clusters · 7 countries")),
        (L("Compliant"), f"{tot[0]}", L("{p}% of high items").format(p=f"{tot[0] / sum(tot) * 100:.0f}"), STATUS_COLORS["Compliant"]),
        (L("Critical gaps"), f"{tot[1] + tot[2]}",
         L("{nc} non-compliant + {p} partially compliant").format(nc=tot[2], p=tot[1]), DSS_RED),
        (L("Non-compliant"), f"{tot[2]}", L("{p}% of high items").format(p=f"{tot[2] / sum(tot) * 100:.0f}"),
         STATUS_COLORS["Non-compliant"]),
        (L("Partially compliant"), f"{tot[1]}", L("{p}% of high items").format(p=f"{tot[1] / sum(tot) * 100:.0f}"), "#D9822B"),
    ])

    w1, w2 = st.columns([1.55, 1])
    with w1:
        st.markdown(f"**{L('Compliance status by high criticality per type of business in the different clusters')}**")
        st.plotly_chart(C.global_high_chart(gh, height=520), width="stretch", config=C.CONFIG, key="gl_main")
    with w2:
        st.markdown(gap_panel_html("High critical compliance gaps", DECK["global_gaps"]["groups"]), unsafe_allow_html=True)

    section(esc(L("High criticality by cluster")), esc(L("The same high-criticality results split into one chart per cluster.")))
    st.plotly_chart(C.business_high_multiples(DECK["cluster_figures"], CLUSTER_ORDER), width="stretch",
                    config=C.CONFIG, key="gl_multi")

    y1, y2 = st.columns([1, 1])
    with y1:
        st.markdown(f"**{L('High-criticality compliance mix per cluster')}**")
        data = [[sum(DECK["cluster_figures"][c][b]["High"][i] for b in DECK["cluster_figures"][c]) for i in range(3)]
                for c in CLUSTER_ORDER]
        st.plotly_chart(C.share_bars([L(c) for c in CLUSTER_ORDER], data, height=260), width="stretch",
                        config=C.CONFIG, key="gl_share")
    with y2:
        st.markdown(f"**{L('High-criticality compliance mix per type of business')}** ({L('all clusters')})")
        data = [[sum(r["values"][i] for r in gh if r["business_type"] == b) for i in range(3)] for b in BUSINESS_ORDER]
        st.plotly_chart(C.share_bars([L(b) for b in BUSINESS_ORDER], data, height=260), width="stretch",
                        config=C.CONFIG, key="gl_share2")

    section(esc(L("All criticality levels · clusters side by side")),
            esc(L("High, medium and low criticality per cluster, for context on where the lower-priority gaps sit.")))
    allc = {c: {cr: [sum(DECK["cluster_figures"][c][b][cr][i] for b in DECK["cluster_figures"][c]) for i in range(3)]
                for cr in CRIT_ORDER} for c in CLUSTER_ORDER}
    st.plotly_chart(C.small_multiples([(L(c), allc[c]) for c in CLUSTER_ORDER], cols=4, height_per_row=280),
                    width="stretch", config=C.CONFIG, key="gl_all")

    ex = DECK["exec_summary"]
    section(esc(L(ex.get("title", "Executive summary"))), esc(L("Global Results Presentation, executive summary.")))
    e1, e2 = st.columns(2)
    with e1:
        st.markdown(card("✓ " + L("Strengths"), [L(x) for x in ex["strengths"]], STATUS_COLORS["Compliant"]),
                    unsafe_allow_html=True)
    with e2:
        st.markdown(card("✗ " + L("Key gaps"), [L(x) for x in ex["gaps"]], STATUS_COLORS["Non-compliant"]),
                    unsafe_allow_html=True)

# ── Downloads (every page) ───────────────────────────────────────────────────────
with st.container(key="dlbox"):
    st.markdown(f'<div class="dltitle">⬇ {esc(L("Download the complete data"))}</div>'
                f'<div class="dlsub">{esc(L("Unfiltered records and the tables behind every chart, generated from the same data as this dashboard."))}</div>',
                unsafe_allow_html=True)
    x1, x2, _ = st.columns([1.4, 1.4, 2])
    x1.download_button(L("Complete records (Excel)"), records_xlsx(), "Amara_NZero_Legal_Compliance_Records.xlsx", XLSX,
                       width="stretch", key="dl_records",
                       help=L("Legal requirements (page 1) and the assessed checklist and site-visit report findings (page 2), in original-language and English sheets."))
    x2.download_button(L("Chart data (Excel)"), graphs_xlsx(), "Amara_NZero_Dashboard_Chart_Data.xlsx", XLSX,
                       width="stretch", key="dl_graphs",
                       help=L("One sheet per chart on pages 1–4 with its table and an Excel chart, plus QA reconciliation sheets."))

st.markdown(f"""<div class="footer"><span>{esc(L("Source: dss+ Safety, Legal Compliance & Culture Assessment for Amara NZero — site checklists, site-visit reports, cluster and global results presentations (June 2026). Confidential."))}</span>
<span>{esc(NATIVE_LANG_NAME[lang_choice()])}</span></div>""",
            unsafe_allow_html=True)