"""Amara NZero — Safety & Legal Compliance Assessment dashboard (dss+, June 2026).

Run:  streamlit run app.py
"""
import io
import re

import pandas as pd
import streamlit as st

import charts as C
from core import (AMARA_GREEN, ASSETS, BUSINESS_ORDER, CLUSTER_ORDER, COUNTRY_CODE, CRIT_ORDER, DSS_RED, INK_2,
                  LANG_NAME, MUTED, NAVY, PANEL, STATUS_COLORS, STATUS_ORDER, RT, T, column_labels,
                  counts_from_checklist, esc, flag_html, gap_panel_html, img_b64, is_en, kpi_row, load_all,
                  section, split_regulations, status_pill, translate_df)

st.set_page_config(page_title="Amara NZero · Legal Compliance", page_icon="🛡️", layout="wide",
                   initial_sidebar_state="collapsed")

df, TRMAP, DECK, REPORTS, HEADERS, SITES = load_all()

# ── Styling ──────────────────────────────────────────────────────────────────────
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
.st-key-navbox, .st-key-navbox [data-testid="stElementContainer"], .st-key-navbox [data-testid="stRadio"],
.st-key-langbox [data-testid="stElementContainer"], .st-key-langbox [data-testid="stRadio"] {{ width:100% !important; }}
.st-key-navbox div[role="radiogroup"], .st-key-langbox div[role="radiogroup"] {{
  display:flex !important; flex-wrap:nowrap; gap:10px; width:100%; }}
.st-key-navbox div[role="radiogroup"] > *, .st-key-langbox div[role="radiogroup"] > * {{
  flex:1 1 0; margin:0 !important; display:flex; }}
.st-key-navbox div[role="radiogroup"] label, .st-key-langbox div[role="radiogroup"] label {{
  width:100%; margin:0 !important; display:flex; align-items:center; justify-content:center; cursor:pointer; }}
/* hide the radio circle, keep the text */
.st-key-navbox div[role="radiogroup"] label div:not([data-testid="stMarkdownContainer"]):not(:has([data-testid="stMarkdownContainer"])):not([data-testid="stMarkdownContainer"] *),
.st-key-langbox div[role="radiogroup"] label div:not([data-testid="stMarkdownContainer"]):not(:has([data-testid="stMarkdownContainer"])):not([data-testid="stMarkdownContainer"] *) {{
  display:none !important; }}
.st-key-navbox div[role="radiogroup"] > * {{ background:{PANEL}; border:1px solid #DCDFE6; border-radius:6px;
  min-height:52px; transition:all .15s ease; }}
.st-key-navbox div[role="radiogroup"] > *:hover {{ border-color:{NAVY}; background:#E9EBF1; }}
.st-key-navbox div[role="radiogroup"] label {{ padding:12px 10px; }}
.st-key-navbox div[role="radiogroup"] p {{ font-weight:700; font-size:15px; color:{INK_2}; margin:0; text-align:center; }}
.st-key-navbox div[role="radiogroup"] > *:has(input:checked) {{ background:{NAVY}; border-color:{NAVY};
  box-shadow:inset 0 -4px 0 {AMARA_GREEN}; }}
.st-key-navbox div[role="radiogroup"] > *:has(input:checked) p {{ color:white; }}
.st-key-langbox {{ background:{PANEL}; border:1px solid #DCDFE6; border-radius:6px; padding:6px 8px; }}
.st-key-langbox div[role="radiogroup"] {{ align-items:center; gap:6px; }}
.st-key-langbox div[role="radiogroup"]::before {{ content:"🌐 Translate"; font-size:13px; font-weight:700;
  color:{INK_2}; white-space:nowrap; margin-right:2px; }}
.st-key-langbox div[role="radiogroup"] > * {{ border-radius:5px; background:white; border:1px solid #DCDFE6; }}
.st-key-langbox div[role="radiogroup"] label {{ padding:7px 8px; }}
.st-key-langbox div[role="radiogroup"] p {{ font-size:13.5px; font-weight:600; color:{INK_2}; margin:0; }}
.st-key-langbox div[role="radiogroup"] > *:has(input:checked) {{ background:{AMARA_GREEN}; border-color:{AMARA_GREEN}; }}
.st-key-langbox div[role="radiogroup"] > *:has(input:checked) p {{ color:white; }}
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

# Keep the site selection alive while other pages are shown (widgets not rendered lose their state).
for _k in ("sel_cluster", "sel_country", "sel_site"):
    if _k in st.session_state:
        st.session_state[_k] = st.session_state[_k]

# ── Header ───────────────────────────────────────────────────────────────────────
flags = "".join(flag_html(c, 17) for c in ["ES", "PT", "MX", "CO", "FR", "GR", "IT"])
st.markdown(f"""
<div class="topbar">
  <img class="dss" src="data:image/png;base64,{img_b64(ASSETS / 'dss_logo.png')}" alt="dss+">
  <div class="divider"></div>
  <div style="flex:1">
    <div class="eyebrow">Safety, Legal Compliance &amp; Culture Assessment · June 2026</div>
    <div class="apptitle">Legal &amp; Regulatory Compliance — Amara NZero</div>
    <div class="subtitle"><span class="flagstrip">{flags}</span>&nbsp; 7 countries · 4 clusters · 23 sites assessed</div>
  </div>
  <img class="amara" src="data:image/png;base64,{img_b64(ASSETS / 'amara_logo.png')}" alt="Amara NZero">
</div>
<div class="greenrule"></div>""", unsafe_allow_html=True)

# ── Navigation (four boxes) + translate switch on the same row ───────────────────
PAGES = ["Legal requirements", "Site compliance", "Cluster results", "Global · high criticality"]
nav_col, lang_col = st.columns([5, 1.25], vertical_alignment="center", gap="medium")
with nav_col:
    with st.container(key="navbox"):
        PAGE = st.radio("Section", PAGES, horizontal=True, key="nav", label_visibility="collapsed")
with lang_col:
    with st.container(key="langbox"):
        choice = st.radio("Translate", ["Original", "English"], horizontal=True, key="lang_widget",
                          label_visibility="collapsed",
                          help="Original = language of the source checklists and reports. English = full translation.")
        st.session_state["lang_mode"] = choice or "Original"
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


NO_COMMENTS = '<li style="list-style:none;color:#8A8FA3">No comments recorded</li>'


def lang_badge(langs):
    langs = sorted(set(langs))
    if is_en():
        return "Showing <b>English</b> translation"
    return "Showing <b>original language</b> · " + ", ".join(LANG_NAME.get(l, l) for l in langs)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Identification of legal requirements (general overview, no company performance)
# ══════════════════════════════════════════════════════════════════════════════
if PAGE == PAGES[0]:
    section("Identification of key activities and legal requirements",
            "Legal requirements identified for Amara NZero's activities")

    view = df.copy()
    view["activity_disp"] = view.activity.map(T)
    regs = view.norm.map(split_regulations).explode().dropna()
    kpi_row([
        ("Legal requirements", f"{len(view):,}", "identified across all sites"),
        ("Key activities", f"{view.activity.nunique():,}", "activity groups"),
        ("Regulations referenced", f"{regs.nunique():,}", "laws, decrees, standards"),
        ("Sites", f"{view.site_id.nunique()}", f"{view.country.nunique()} countries"),
        ("Types of business", f"{view.business_type.nunique()}",
         " · ".join(b for b in BUSINESS_ORDER if b in set(view.business_type))),
    ])

    c1, c2 = st.columns([1.3, 1], gap="large")
    with c1:
        st.markdown("**Requirements by country and type of business** · number of legal requirements "
                    "(click a country to focus, click the top bar to go back)")
        st.plotly_chart(C.treemap(view, height=470), width="stretch", config=C.CONFIG, key="t1_tree")
    with c2:
        st.markdown("**Requirements matrix** · country × type of business")
        st.plotly_chart(C.count_matrix(view, height=470), width="stretch", config=C.CONFIG, key="t1_matrix")

    c3, c4 = st.columns([1, 1.3], gap="large")
    with c3:
        st.markdown("**Most-referenced regulations** · number of requirements citing each")
        top = regs.value_counts().head(15)
        st.plotly_chart(C.regulation_bars(top, height=500), width="stretch", config=C.CONFIG, key="t1_regs")
    with c4:
        st.markdown("**Requirements per site** · coloured by type of business")
        st.plotly_chart(C.site_bars(view, height=500), width="stretch", config=C.CONFIG, key="t1_sites")

    # Register: general list of legal requirements, filterable
    section("Legal requirements register", lang_badge(view.lang) +
            " · filter by country, site, type of business, key activity or requirement")
    f1, f2, f3, f4, f5 = st.columns([1, 1.3, 1, 1.5, 1.5])
    with f1:
        r_country = st.multiselect("Country", [c for c in ["Spain", "Portugal", "Mexico", "Colombia", "France", "Greece", "Italy"]],
                                   placeholder="All countries", key="r_country")
    reg = view if not r_country else view[view.country.isin(r_country)]
    with f2:
        r_site = st.multiselect("Site", list(dict.fromkeys(reg.site)), placeholder="All sites", key="r_site")
    reg = reg if not r_site else reg[reg.site.isin(r_site)]
    with f3:
        r_type = st.multiselect("Type of business", [b for b in BUSINESS_ORDER if b in set(reg.business_type)],
                                placeholder="All types", key="r_type")
    reg = reg if not r_type else reg[reg.business_type.isin(r_type)]
    with f4:
        r_act = st.multiselect("Key activity", sorted(set(reg.activity_disp)), placeholder="All activities", key="r_act")
    reg = reg if not r_act else reg[reg.activity_disp.isin(r_act)]
    with f5:
        r_q = st.text_input("Requirement / regulation contains", placeholder="e.g. ATEX, RD 486/1997, contractor…",
                            key="r_q")
    if r_q:
        q = r_q.lower()
        mask = pd.Series(False, index=reg.index)
        for c in ["requirement", "norm", "activity"]:
            mask |= reg[c].str.lower().str.contains(q, regex=False)
            mask |= reg[c].map(lambda v: TRMAP.get(v, v)).str.lower().str.contains(q, regex=False)
        reg = reg[mask]

    fields = ["country", "site", "business_type", "id", "activity", "requirement", "norm"]
    out = translate_df(reg[fields], ["activity", "requirement", "norm"])
    labels = column_labels(fields, reg.lang, list(reg.site_id.unique()))
    out = out.rename(columns=labels)
    st.dataframe(out, hide_index=True, height=600, width="stretch", row_height=40,
                 column_config={labels["country"]: st.column_config.TextColumn(labels["country"], width="small"),
                                labels["site"]: st.column_config.TextColumn(labels["site"], width="medium"),
                                labels["business_type"]: st.column_config.TextColumn(labels["business_type"], width="medium"),
                                labels["id"]: st.column_config.TextColumn(labels["id"], width="small"),
                                labels["activity"]: st.column_config.TextColumn(labels["activity"], width="medium"),
                                labels["requirement"]: st.column_config.TextColumn(labels["requirement"], width="large"),
                                labels["norm"]: st.column_config.TextColumn(labels["norm"], width="large")})
    d0, d1, d2 = st.columns([4, 1, 1])
    d0.markdown(f'<div class="note">{len(out):,} of {len(view):,} requirements shown. Compliance results per site are '
                'in <b>Site compliance</b>.</div>', unsafe_allow_html=True)
    d1.download_button("⬇ Excel", to_excel(out, "Legal requirements"), "amara_legal_requirements.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
    d2.download_button("⬇ CSV", out.to_csv(index=False).encode("utf-8-sig"), "amara_legal_requirements.csv",
                       "text/csv", width="stretch")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Site drill-down
# ══════════════════════════════════════════════════════════════════════════════
if PAGE == PAGES[1]:
    section("Legal compliance assessment by site",
            "Choose a region, country and site to see its compliance results, key gaps, the site-visit findings and the "
            "full assessed checklist.")
    s1, s2, s3 = st.columns([1, 1, 1.6])
    with s1:
        sel_cluster = st.selectbox("Region (cluster)", CLUSTER_ORDER, key="sel_cluster")
    with s2:
        countries = [c for c in ["Spain", "Portugal", "Mexico", "Colombia", "France", "Greece", "Italy"]
                     if c in set(SITES[SITES.cluster == sel_cluster].country)]
        sel_country = st.selectbox("Country", countries, key="sel_country",
                                   format_func=lambda c: f"{c}  ({(SITES.country == c).sum()} site{'s' if (SITES.country == c).sum() > 1 else ''})")
    with s3:
        site_opts = SITES[SITES.country == sel_country]
        sel_site = st.selectbox("Site", list(site_opts.site_id), key="sel_site",
                                format_func=lambda s: f"{SITES.set_index('site_id').site[s]} · {SITES.set_index('site_id').business_type[s]}")

    srow = SITES.set_index("site_id").loc[sel_site]
    sdf = df[df.site_id == sel_site].copy()
    rep = REPORTS.get(sel_site, {})
    visit = rep.get("visit_date", "")
    st.markdown(f"""<div class="sitebanner"><div>
        <div class="t">{flag_html(COUNTRY_CODE[srow.country], 20)} {esc(srow.site)}</div>
        <div class="m">{srow.country} · {srow.cluster} cluster · Type of business: <b>{srow.business_type}</b>
        {' · Visit: ' + esc(visit) if visit else ''}</div></div>
        <div><span class="chip">Checklist language: {LANG_NAME.get(srow.lang, srow.lang)}</span>
        <span class="chip">{len(sdf)} requirements assessed</span></div></div>""", unsafe_allow_html=True)

    sc = sdf.status_level.value_counts()
    assessed = int(sum(sc.get(k, 0) for k in STATUS_ORDER))
    hi_gap = int(((sdf.criticality_level == "High") & sdf.status_level.isin(["Non-compliant", "Partially compliant"])).sum())
    pct = lambda k: f"{sc.get(k, 0) / assessed * 100:.0f}% of assessed" if assessed else ""
    kpi_row([
        ("Requirements", f"{len(sdf)}", f"{assessed} with a compliance result"),
        ("Compliant", f"{sc.get('Compliant', 0)}", pct("Compliant"), STATUS_COLORS["Compliant"]),
        ("Partially compliant", f"{sc.get('Partially compliant', 0)}", pct("Partially compliant"), "#D9822B"),
        ("Non-compliant", f"{sc.get('Non-compliant', 0)}", pct("Non-compliant") + (" · incl. pending evidence" if sdf.status.str.lower().str.startswith(('pend',)).any() else ""), STATUS_COLORS["Non-compliant"]),
        ("High-criticality gaps", f"{hi_gap}", "high criticality, not fully compliant", DSS_RED),
    ])

    # Row 1: official chart + key gaps panel
    g1, g2 = st.columns([1.05, 1])
    with g1:
        st.markdown("**Compliance status by criticality**")
        if sel_site in DECK["site_figures"]:
            figd = DECK["site_figures"][sel_site]
            src = "Source: figures as reported in the dss+ cluster presentation (June 2026)."
        else:
            figd = counts_from_checklist(sdf)
            src = "Source: calculated from the site checklist (this site has no separate chart in the cluster deck)."
            grp = next((g for g in DECK["group_figures"].values() if sel_site in g["sites"]), None)
            if grp:
                h = grp["figures"]
                src += (f" The deck reports <b>{grp['label']}</b> together: High {h['High'][0]}/{h['High'][1]}/{h['High'][2]}, "
                        f"Medium {h['Medium'][0]}/{h['Medium'][1]}/{h['Medium'][2]}, Low {h['Low'][0]}/{h['Low'][1]}/{h['Low'][2]} "
                        "(compliant / partial / non-compliant) — see Cluster results.")
        st.plotly_chart(C.criticality_stack(figd, height=380), width="stretch", config=C.CONFIG, key="site_crit")
        st.markdown(f'<div class="srcnote">{src}</div>', unsafe_allow_html=True)
    with g2:
        gaps = DECK["site_gaps"].get(sel_site)
        if gaps:
            st.markdown(gap_panel_html("Key compliance gaps", gaps), unsafe_allow_html=True)
            st.markdown('<div class="srcnote" style="margin-top:6px">From the cluster presentation (English).</div>',
                        unsafe_allow_html=True)
        else:
            hi = sdf[(sdf.criticality_level == "High") & (sdf.status_level == "Non-compliant")]
            items = [f"<b>{esc(T(a))}</b>: {esc(T(r))[:260]}" for a, r in zip(hi.activity, hi.reason)] or ["None recorded"]
            st.markdown(gap_panel_html("Key compliance gaps (high criticality, from checklist)",
                                       [("High criticality – not compliant", items[:12])]), unsafe_allow_html=True)

    # Row 2: status donut + activity hotspot
    a1, a2 = st.columns([0.8, 1.4])
    with a1:
        st.markdown("**Overall status of all checklist items**")
        st.plotly_chart(C.status_donut(sc.to_dict(), height=330), width="stretch", config=C.CONFIG, key="site_donut")
        crit_tab = (sdf.pivot_table(index="criticality_level", columns="status_level", values="id", aggfunc="count", fill_value=0)
                       .reindex([c for c in CRIT_ORDER + ["Not rated"] if c in set(sdf.criticality_level)]))
        crit_tab = crit_tab[[c for c in STATUS_ORDER + ["Not applicable", "Not assessed"] if c in crit_tab.columns]]
        st.markdown('<div class="note">Checklist records by criticality and status</div>', unsafe_allow_html=True)
        st.dataframe(crit_tab.rename_axis("Criticality"), width="stretch")
    with a2:
        st.markdown("**Compliance by key activity** · where the gaps concentrate (checklist)")
        act = (sdf[sdf.status_level.isin(STATUS_ORDER)]
               .assign(act=lambda d: d.activity.map(T).str.slice(0, 55))
               .pivot_table(index="act", columns="status_level", values="id", aggfunc="count", fill_value=0))
        for s in STATUS_ORDER:
            if s not in act.columns:
                act[s] = 0
        act = act[STATUS_ORDER].sort_values(["Non-compliant", "Partially compliant"], ascending=False)
        if act.empty:
            st.info("No assessed items with a compliance result.")
        else:
            st.plotly_chart(C.activity_bars(act, height=max(330, 70 + 26 * len(act))), width="stretch",
                            config=C.CONFIG, key="site_act")

    # Row 3: site-visit report — key activities assessment (deck/report layout)
    if rep:
        section("Legal compliance assessment · site-visit report",
                f"Key activities, governing regulations, compliance indicator and findings — from "
                f"<i>{esc(rep.get('report_file', ''))}</i>. "
                + ("" if rep.get("report_language") == "en" or is_en() else "Original language shown; switch to English with the Translate control."))
        stf = st.multiselect("Show status", ["Compliant", "Partially compliant", "Non-compliant", "Not assessed"],
                             default=["Compliant", "Partially compliant", "Non-compliant", "Not assessed"], key="rep_status")
        rows_html = ""
        for ka in rep.get("key_activities", []):
            if ka.get("status") not in stf:
                continue
            col = STATUS_COLORS.get(ka.get("status"), "#D9DCE2")
            regs_html = "".join(f"<li>{esc(r)}</li>" for r in ka.get("regulations", [])[:12])
            com = "".join(f"<li>{esc(RT(c))}</li>".replace("\n", "<br>") for c in ka.get("comments", []))
            com = com.replace("<li>", '<li style="margin:2px 0">')
            com = com or NO_COMMENTS
            rows_html += (f'<tr><td class="act" style="border-left-color:{col}"><b>{esc(RT(ka["activity"]))}</b>'
                          f'<ul>{regs_html}</ul></td>'
                          f'<td class="st"><span class="dot" style="background:{col}"></span><br>'
                          f'<span style="font-size:11.5px;color:{MUTED}">{ka.get("status")}</span></td>'
                          f'<td><ul>{com}</ul></td></tr>')
        st.markdown(f'<div class="scrollbox"><table class="assess"><thead><tr><th>Key activity &amp; regulations</th>'
                    f'<th style="text-align:center">Compliance</th><th>Comments / missing evidence</th></tr></thead>'
                    f'<tbody>{rows_html}</tbody></table></div>', unsafe_allow_html=True)

        e1, e2 = st.columns(2)
        with e1:
            lis = "".join(f"<li>{esc(RT(x))}</li>" for x in rep.get("summary_strengths", [])) or "<li>—</li>"
            st.markdown(f'<div class="card" style="border-top:4px solid {STATUS_COLORS["Compliant"]}"><h4>✓ Strengths</h4>'
                        f'<ul>{lis}</ul></div>', unsafe_allow_html=True)
        with e2:
            lis = "".join(f"<li>{esc(RT(x))}</li>" for x in rep.get("summary_improvements", [])) or "<li>—</li>"
            st.markdown(f'<div class="card" style="border-top:4px solid {STATUS_COLORS["Non-compliant"]}"><h4>✗ Areas for improvement</h4>'
                        f'<ul>{lis}</ul></div>', unsafe_allow_html=True)
        qw, rc = rep.get("quick_wins", []), rep.get("recommendations", [])
        if qw or rc:
            st.write("")
            q1, q2 = st.columns(2)
            with q1:
                lis = "".join(f"<li>{esc(RT(x)).replace(chr(10), '<br>')}</li>" for x in qw) or "<li>—</li>"
                st.markdown(f'<div class="card" style="border-top:4px solid {AMARA_GREEN}"><h4>⚡ Quick wins</h4><ul>{lis}</ul></div>',
                            unsafe_allow_html=True)
            with q2:
                lis = "".join(f"<li>{esc(RT(x)).replace(chr(10), '<br>')}</li>" for x in rc) or "<li>—</li>"
                st.markdown(f'<div class="card" style="border-top:4px solid {NAVY}"><h4>➜ Recommendations</h4><ul>{lis}</ul></div>',
                            unsafe_allow_html=True)

    # Row 4: full checklist, Excel-style
    section("Assessed checklist · all records for this site", lang_badge([srow.lang]))
    k1, k2, k3 = st.columns([1, 1.3, 2])
    with k1:
        fc = st.multiselect("Criticality", [c for c in CRIT_ORDER + ["Not rated"] if c in set(sdf.criticality_level)],
                            key="ck_crit", placeholder="All")
    with k2:
        fs = st.multiselect("Compliance status", [s for s in STATUS_ORDER + ["Not applicable", "Not assessed"]
                                                   if s in set(sdf.status_level)], key="ck_status", placeholder="All")
    with k3:
        fq = st.text_input("Search in this checklist", key="ck_q", placeholder="keyword…")
    cdf = sdf
    if fc:
        cdf = cdf[cdf.criticality_level.isin(fc)]
    if fs:
        cdf = cdf[cdf.status_level.isin(fs)]
    if fq:
        m = pd.Series(False, index=cdf.index)
        for c in ["activity", "norm", "requirement", "question", "evidence", "reason", "notes"]:
            m |= cdf[c].str.lower().str.contains(fq.lower(), regex=False) | cdf[c].map(lambda v: TRMAP.get(v, v)).str.lower().str.contains(fq.lower(), regex=False)
        cdf = cdf[m]
    fields = ["id", "activity", "norm", "eu_directive", "requirement", "question", "evidence", "notes", "documents",
              "criticality", "status", "status_level", "reason", "amara_comments", "missing_document", "responsible",
              "frequency"]
    fields = [f for f in fields if (sdf[f] != "").any()]
    out = translate_df(cdf[fields], [f for f in fields if f not in ("id", "status_level")])
    labels = column_labels(fields, [srow.lang], [sel_site])
    out = out.rename(columns=labels)
    stat_col = labels["status_level"]

    def _color_status(v):
        c = STATUS_COLORS.get(v)
        return f"background-color:{c}33; color:{NAVY}; font-weight:600" if c else ""

    styled = out.style.map(_color_status, subset=[stat_col])
    wide = {labels[f]: st.column_config.TextColumn(labels[f], width="large") for f in
            ["requirement", "question", "evidence", "reason", "notes", "norm", "amara_comments", "documents"] if f in labels}
    st.dataframe(styled, hide_index=True, height=520, width="stretch", row_height=38,
                 column_config={**wide, labels["id"]: st.column_config.TextColumn(labels["id"], width="small")})
    st.markdown(f'<div class="srcnote">{len(out)} of {len(sdf)} records. "{stat_col}" maps each original status to '
                'Compliant / Partially compliant / Non-compliant (incl. pending evidence) / Not applicable. '
                'France checklists record status by cell colour; it has been read from the colour.</div>',
                unsafe_allow_html=True)
    d1, d2, _ = st.columns([1, 1, 4])
    d1.download_button("⬇ Excel", to_excel(out, sel_site), f"amara_{sel_site}_checklist.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch", key="dl_site_x")
    d2.download_button("⬇ CSV", out.to_csv(index=False).encode("utf-8-sig"), f"amara_{sel_site}_checklist.csv", "text/csv",
                       width="stretch", key="dl_site_c")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Cluster of the selected site
# ══════════════════════════════════════════════════════════════════════════════
if PAGE == PAGES[2]:
    cl = SITES.set_index("site_id").cluster[st.session_state.get("sel_site", SITES.site_id.iloc[0])]
    meta = DECK["cluster_meta"][cl]
    cfig = DECK["cluster_figures"][cl]
    section(f"{cl} cluster results",
            f"Cluster of the site selected in Site compliance ({esc(SITES.set_index('site_id').site[st.session_state.get('sel_site', SITES.site_id.iloc[0])])}). "
            "Change the site there to switch cluster. Figures as presented in the dss+ cluster results (English).")
    st.markdown(f"""<div class="sitebanner"><div><div class="t">{''.join(flag_html(f, 22) for f in meta['flags'])} {cl}</div>
        <div class="m">{esc(meta['scope'])}</div></div><div class="m" style="max-width:640px">{esc(meta['headline'])}</div></div>""",
                unsafe_allow_html=True)

    tot = [sum(cfig[b][c][i] for b in cfig for c in CRIT_ORDER) for i in range(3)]
    hi = [sum(cfig[b]["High"][i] for b in cfig) for i in range(3)]
    kpi_row([
        ("Requirements assessed", f"{sum(tot)}", f"{len(cfig)} type{'s' if len(cfig) > 1 else ''} of business"),
        ("Compliant", f"{tot[0]}", f"{tot[0] / max(1, sum(tot)) * 100:.0f}% of assessed", STATUS_COLORS["Compliant"]),
        ("High criticality · non-compliant", f"{hi[2]}", "full non-compliance", STATUS_COLORS["Non-compliant"]),
        ("High criticality · partial", f"{hi[1]}", "limited or incomplete evidence", "#D9822B"),
        ("High criticality · compliant", f"{hi[0]}", f"{hi[0] / max(1, sum(hi)) * 100:.0f}% of high items", STATUS_COLORS["Compliant"]),
    ])

    m1, m2 = st.columns([1.55, 1])
    with m1:
        st.markdown(f"**Compliance status per criticality of business in the {cl} cluster**")
        st.plotly_chart(C.cluster_business_stack(cfig, height=470), width="stretch", config=C.CONFIG, key="cl_main")
    with m2:
        st.markdown(gap_panel_html("High critical compliance gaps",
                                   [(f"{h}", b) for h, b in DECK["cluster_gaps"][cl]]), unsafe_allow_html=True)

    # Per-site small multiples
    csites = SITES[SITES.cluster == cl]
    items, used_group = [], set()
    for sid in csites.site_id:
        if sid in DECK["site_figures"]:
            items.append((SITES.set_index("site_id").site[sid], DECK["site_figures"][sid]))
        else:
            grp = next((k for k, g in DECK["group_figures"].items() if sid in g["sites"]), None)
            if grp and grp not in used_group:
                used_group.add(grp)
                items.append(("Mexico in-house services*", DECK["group_figures"][grp]["figures"]))
    if items:
        section("Compliance status by criticality · per site", "One panel per assessed site, as in the cluster presentation.")
        st.plotly_chart(C.small_multiples(items, cols=min(5, len(items)), height_per_row=260), width="stretch",
                        config=C.CONFIG, key="cl_sm")
        if used_group:
            st.markdown('<div class="srcnote">* Iberdrola, Schneider and Braskem are reported together in the deck. '
                        'Chetumal and Altamira were assessed remotely and are not charted in the deck (see the Site tab).</div>',
                        unsafe_allow_html=True)

    b1, b2 = st.columns([1, 1.1])
    with b1:
        st.markdown("**Compliance mix by type of business** (all criticality levels)")
        types = [b for b in BUSINESS_ORDER if b in cfig]
        data = [[sum(cfig[b][c][i] for c in CRIT_ORDER) for i in range(3)] for b in types]
        st.plotly_chart(C.share_bars(types, data), width="stretch", config=C.CONFIG, key="cl_share")
    with b2:
        st.markdown("**Share compliant by site and criticality** — red cells are the priority areas")
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
            st.plotly_chart(C.heat_rate(rows, CRIT_ORDER, z, txt, height=90 + 34 * len(rows)), width="stretch",
                            config=C.CONFIG, key="cl_heat")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Global, highest criticality
# ══════════════════════════════════════════════════════════════════════════════
if PAGE == PAGES[3]:
    section("Global results · high criticality",
            "High-criticality legal requirements across all clusters by type of business, as presented in the Global "
            "Results Presentation (June 2026, English).")
    gh = DECK["global_high"]
    tot = [sum(r["values"][i] for r in gh) for i in range(3)]
    kpi_row([
        ("High-criticality items", f"{sum(tot)}", "across 4 clusters · 7 countries"),
        ("Compliant", f"{tot[0]}", f"{tot[0] / sum(tot) * 100:.0f}% of high items", STATUS_COLORS["Compliant"]),
        ("Critical gaps", f"{tot[1] + tot[2]}", f"{tot[2]} non-compliant + {tot[1]} partially compliant", DSS_RED),
        ("Non-compliant", f"{tot[2]}", f"{tot[2] / sum(tot) * 100:.0f}% of high items", STATUS_COLORS["Non-compliant"]),
        ("Partially compliant", f"{tot[1]}", f"{tot[1] / sum(tot) * 100:.0f}% of high items", "#D9822B"),
    ])

    w1, w2 = st.columns([1.55, 1])
    with w1:
        st.markdown("**Compliance status by <u>high criticality</u> per type of business in the different clusters**",
                    unsafe_allow_html=True)
        st.plotly_chart(C.global_high_chart(gh, height=520), width="stretch", config=C.CONFIG, key="gl_main")
    with w2:
        st.markdown(gap_panel_html("High critical compliance gaps", [(h, b) for h, b in DECK["global_gaps"]]),
                    unsafe_allow_html=True)

    section("High criticality by cluster", "The same high-criticality results split into one chart per cluster.")
    st.plotly_chart(C.business_high_multiples(DECK["cluster_figures"], CLUSTER_ORDER,
                                              {c: DECK["cluster_meta"][c]["flags"] for c in CLUSTER_ORDER}),
                    width="stretch", config=C.CONFIG, key="gl_multi")

    y1, y2 = st.columns([1, 1])
    with y1:
        st.markdown("**High-criticality compliance mix per cluster**")
        data = [[sum(DECK["cluster_figures"][c][b]["High"][i] for b in DECK["cluster_figures"][c]) for i in range(3)]
                for c in CLUSTER_ORDER]
        st.plotly_chart(C.share_bars(CLUSTER_ORDER, data, height=260), width="stretch", config=C.CONFIG, key="gl_share")
    with y2:
        st.markdown("**High-criticality compliance mix per type of business** (all clusters)")
        data = [[sum(r["values"][i] for r in gh if r["business_type"] == b) for i in range(3)] for b in BUSINESS_ORDER]
        st.plotly_chart(C.share_bars(BUSINESS_ORDER, data, height=260), width="stretch", config=C.CONFIG, key="gl_share2")

    section("All criticality levels · clusters side by side",
            "High, medium and low criticality per cluster, for context on where the lower-priority gaps sit.")
    allc = {c: {cr: [sum(DECK["cluster_figures"][c][b][cr][i] for b in DECK["cluster_figures"][c]) for i in range(3)]
                for cr in CRIT_ORDER} for c in CLUSTER_ORDER}
    st.plotly_chart(C.small_multiples([(c, allc[c]) for c in CLUSTER_ORDER], cols=4, height_per_row=280),
                    width="stretch", config=C.CONFIG, key="gl_all")

    ex = DECK["exec_summary"]
    e1, e2 = st.columns(2)
    with e1:
        st.markdown(f'<div class="card" style="border-top:4px solid {STATUS_COLORS["Compliant"]}"><h4>✓ Strengths</h4><ul>'
                    + "".join(f"<li>{esc(x)}</li>" for x in ex["strengths"]) + "</ul></div>", unsafe_allow_html=True)
    with e2:
        st.markdown(f'<div class="card" style="border-top:4px solid {STATUS_COLORS["Non-compliant"]}"><h4>✗ Key gaps</h4><ul>'
                    + "".join(f"<li>{esc(x)}</li>" for x in ex["gaps"]) + "</ul></div>", unsafe_allow_html=True)

st.markdown(f"""<div class="footer"><span>Source: dss+ Safety, Legal Compliance &amp; Culture Assessment for Amara NZero —
site checklists, site-visit reports, cluster and global results presentations (June 2026). Confidential.</span>
<span>{'English translation' if is_en() else 'Original language'}</span></div>""", unsafe_allow_html=True)