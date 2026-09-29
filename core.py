"""Data loading, translation helpers, theme constants and shared HTML snippets."""
import base64
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"

# ── Palette taken from the dss+ / Amara NZero decks ─────────────────────────────
NAVY = "#1B1F3B"
INK_2 = "#4A4F66"
MUTED = "#8A8FA3"
PANEL = "#F2F3F5"
GRID = "#E6E8EE"
DSS_RED = "#E1261C"
AMARA_GREEN = "#009B3A"
AMARA_LIME = "#C4D600"
STATUS_ORDER = ["Compliant", "Partially compliant", "Non-compliant"]
STATUS_COLORS = {
    "Compliant": "#1FA276",
    "Partially compliant": "#F0A02C",
    "Non-compliant": "#E24B47",
    "Not applicable": "#B8BCC6",
    "Not assessed": "#D9DCE2",
}
CRIT_ORDER = ["High", "Medium", "Low"]
CRIT_COLORS = {"High": "#1B1F3B", "Medium": "#6B7093", "Low": "#B3B6C9", "Not rated": "#DADCE5"}
BUSINESS_ORDER = ["Office", "EPC", "Factory", "Warehouse", "Services"]
CLUSTER_ORDER = ["Spain & Portugal", "Mexico & Colombia", "France", "Greece & Italy"]
COUNTRY_CODE = {"Spain": "ES", "Portugal": "PT", "Mexico": "MX", "Colombia": "CO", "France": "FR",
                "Greece": "GR", "Italy": "IT"}
LANG_NAME = {"es": "Spanish", "fr": "French", "it": "Italian", "pt": "Portuguese", "en": "English"}

FIELD_LABELS_EN = {
    "country": "Country", "cluster": "Region (cluster)", "site": "Site", "business_type": "Type of business",
    "id": "ID", "installation": "Installation", "facility_type": "Installation type", "activity": "Key activity",
    "norm": "Standard / Reference", "eu_directive": "EU Directive / Regulation", "requirement": "Legal requirement",
    "question": "Assessment question", "evidence": "Required evidence", "notes": "Notes",
    "documents": "Documents or certifications required", "criticality": "Criticality level",
    "status": "Legal compliance status", "reason": "Reason for status", "amara_comments": "Amara team comments",
    "frequency": "Frequency / Legal deadline", "missing_document": "Missing document", "responsible": "Responsible",
    "status_level": "Status (normalised)", "criticality_level": "Criticality (normalised)",
}


# ── Flags (inline SVG so they render everywhere, offline) ───────────────────────
def _svg(body, w=30, h=20):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'


FLAG_SVG = {
    "ES": _svg('<rect width="30" height="20" fill="#AA151B"/><rect y="5" width="30" height="10" fill="#F1BF00"/>'),
    "PT": _svg('<rect width="30" height="20" fill="#DA291C"/><rect width="12" height="20" fill="#046A38"/>'
               '<circle cx="12" cy="10" r="4" fill="#FFE900" stroke="#DA291C" stroke-width="0.8"/>'),
    "MX": _svg('<rect width="10" height="20" fill="#006847"/><rect x="10" width="10" height="20" fill="#fff"/>'
               '<rect x="20" width="10" height="20" fill="#CE1126"/><circle cx="15" cy="10" r="2.6" fill="#8C5A2B"/>'),
    "CO": _svg('<rect width="30" height="20" fill="#FCD116"/><rect y="10" width="30" height="5" fill="#003893"/>'
               '<rect y="15" width="30" height="5" fill="#CE1126"/>'),
    "FR": _svg('<rect width="10" height="20" fill="#0055A4"/><rect x="10" width="10" height="20" fill="#fff"/>'
               '<rect x="20" width="10" height="20" fill="#EF4135"/>'),
    "IT": _svg('<rect width="10" height="20" fill="#009246"/><rect x="10" width="10" height="20" fill="#fff"/>'
               '<rect x="20" width="10" height="20" fill="#CE2B37"/>'),
    "GR": _svg('<rect width="30" height="20" fill="#0D5EAF"/>'
               + "".join(f'<rect y="{y:.3f}" width="30" height="2.222" fill="#fff"/>' for y in [2.222, 6.667, 11.111, 15.556])
               + '<rect width="11.111" height="11.111" fill="#0D5EAF"/><rect x="4.444" width="2.222" height="11.111" fill="#fff"/>'
               '<rect y="4.444" width="11.111" height="2.222" fill="#fff"/>'),
}


def flag_uri(code):
    return "data:image/svg+xml;base64," + base64.b64encode(FLAG_SVG[code].encode()).decode()


def flag_html(code, h=16):
    return (f'<img src="{flag_uri(code)}" style="height:{h}px;border-radius:2px;'
            f'box-shadow:0 0 0 1px rgba(0,0,0,.12);vertical-align:-3px;margin-right:4px" alt="{code}">')


def img_b64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


# ── Data ─────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_all():
    df = pd.DataFrame(json.loads((DATA / "checklist.json").read_text(encoding="utf-8")))
    for c in FIELD_LABELS_EN:
        if c not in df.columns:
            df[c] = ""
    df = df.fillna("")
    trmap = json.loads((DATA / "translations_en.json").read_text(encoding="utf-8"))
    deck = json.loads((DATA / "deck_results.json").read_text(encoding="utf-8"))
    reports = json.loads((DATA / "site_reports.json").read_text(encoding="utf-8"))
    headers = json.loads((DATA / "header_labels.json").read_text(encoding="utf-8"))
    sites = (df.groupby("site_id", sort=False)
               .agg(site=("site", "first"), country=("country", "first"), cluster=("cluster", "first"),
                    business_type=("business_type", "first"), lang=("lang", "first"), n=("id", "size"))
               .reset_index())
    return df, trmap, deck, reports, headers, sites


def is_en():
    return st.session_state.get("lang_mode", "Original") == "English"


def T(text):
    """Translate a checklist value when English mode is on."""
    if not is_en() or not isinstance(text, str) or not text:
        return text
    _, trmap, *_ = load_all()
    return trmap.get(text, trmap.get(text.strip(), text))


def RT(item):
    """Pick the right language from a report item {'en':..., 'orig':...}."""
    if isinstance(item, dict):
        return item.get("en") if is_en() else (item.get("orig") or item.get("en"))
    return item


def translate_df(df, cols):
    if not is_en():
        return df
    out = df.copy()
    _, trmap, *_ = load_all()
    for c in cols:
        if c in out.columns:
            out[c] = out[c].map(lambda v: trmap.get(v, trmap.get(v.strip(), v)) if isinstance(v, str) and v else v)
    return out


def column_labels(fields, langs, site_ids):
    """Headers in the original language when the view holds a single non-English source language."""
    _, _, _, _, headers, _ = load_all()
    labels = {f: FIELD_LABELS_EN.get(f, f) for f in fields}
    if is_en() or len(set(langs)) != 1 or list(set(langs))[0] == "en":
        return labels
    for sid in site_ids:  # first site that carries each header
        for f in fields:
            h = headers.get(sid, {}).get(f)
            if h and labels[f] == FIELD_LABELS_EN.get(f, f):
                labels[f] = re.sub(r"\s+", " ", h).strip()
    return labels


def split_regulations(norm_text):
    """Split a 'Norma / Referencia' cell into individual regulation references."""
    if not norm_text:
        return []
    parts = re.split(r"\s\+\s|\+|;|\n|\s—\s|\s–\s(?=[A-Z])", norm_text)
    out = []
    for p in parts:
        p = re.sub(r"\s*\(.*?\)\s*", " ", p).strip(" .,:-–—")
        p = re.sub(r"\s+", " ", p)
        if 3 <= len(p) <= 60 and re.search(r"\d", p):
            out.append(p)
    return out


def counts_from_checklist(sub):
    """[compliant, partial, non-compliant] per criticality from checklist rows."""
    res = {}
    for c in CRIT_ORDER:
        s = sub[sub.criticality_level == c].status_level.value_counts()
        res[c] = [int(s.get(k, 0)) for k in STATUS_ORDER]
    return res


# ── HTML helpers ─────────────────────────────────────────────────────────────────
def kpi(label, value, sub="", color=NAVY):
    return (f'<div class="kpi"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="color:{color}">{value}</div>'
            f'<div class="kpi-sub">{sub}</div></div>')


def kpi_row(items):
    st.markdown('<div class="kpi-row">' + "".join(kpi(*i) for i in items) + "</div>", unsafe_allow_html=True)


def status_pill(status):
    col = STATUS_COLORS.get(status, "#D9DCE2")
    return f'<span class="pill" style="background:{col}1f;color:{NAVY};border:1px solid {col}"><i style="background:{col}"></i>{status}</span>'


def section(title, sub=""):
    st.markdown(f'<div class="section"><h3>{title}</h3>{f"<p>{sub}</p>" if sub else ""}</div>',
                unsafe_allow_html=True)


def gap_panel_html(title, groups):
    """Grey 'Key compliance gaps' panel as used on the right of the deck slides."""
    html = f'<div class="gap-panel"><div class="gap-title">{title}</div>'
    for heading, bullets in groups:
        tone = DSS_RED if ("not compliant" in heading.lower() or "key gaps" in heading.lower()) else "#D9822B"
        if "partial" in heading.lower():
            tone = "#D9822B"
        html += f'<div class="gap-h" style="color:{tone}">{heading}</div><ul>'
        html += "".join(f"<li>{b}</li>" for b in bullets) + "</ul>"
    return html + "</div>"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
