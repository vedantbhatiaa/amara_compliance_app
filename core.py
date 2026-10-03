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
NATIVE_LANG_NAME = {"es": "Español", "fr": "Français", "it": "Italiano", "pt": "Português", "en": "English"}
# Translate dropdown (owner decision, v0.5): the options are the languages of the country / cluster on screen plus
# English — e.g. a Spanish site: Español | English; the Spain & Portugal cluster: Español | Português | English.
# Checklists and reports are shown as written when they are in the chosen language; every English-authored text
# (interface, deck insights, English report findings) is translated via data/lang/<code>.json.
LANG_CHOICES = ["es", "pt", "fr", "it", "en"]
LANG_COUNTRIES = {"en": "", "es": "ES · MX · CO", "pt": "PT", "fr": "FR", "it": "IT"}
# Language of each country's source documents. Greece's checklist and report were written in English (kept as is).
COUNTRY_LANG = {"Spain": "es", "Portugal": "pt", "Mexico": "es", "Colombia": "es", "France": "fr",
                "Greece": "en", "Italy": "it"}
# Country labels for the page-1 filter: constant in every language (Streamlit keeps multiselect selections as labels).
NATIVE_COUNTRY_NAME = {"Spain": "España / Spain", "Portugal": "Portugal", "Mexico": "México / Mexico",
                       "Colombia": "Colombia", "France": "France", "Greece": "Ελλάδα / Greece", "Italy": "Italia / Italy"}
COUNTRY_ORDER = ["Spain", "Portugal", "Mexico", "Colombia", "France", "Greece", "Italy"]

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
    i18n = {}
    sites = (df.groupby("site_id", sort=False)
               .agg(site=("site", "first"), country=("country", "first"), cluster=("cluster", "first"),
                    business_type=("business_type", "first"), lang=("lang", "first"), n=("id", "size"))
               .reset_index())
    return df, trmap, deck, reports, headers, sites, i18n


def lang_choice():
    """Language code chosen in the Translate dropdown (default English)."""
    return st.session_state.get("lang_code", "en")


def is_en():
    return lang_choice() == "en"


def page_countries():
    """Countries on screen: page 1 = countries filtered in the register (all if none); page 2 = the selected site's
    country; page 3 = the countries of that site's cluster; page 4 = all countries."""
    sites = load_all()[5]
    page = st.session_state.get("nav", "Legal requirements")
    if page == "Legal requirements":
        return st.session_state.get("r_country") or COUNTRY_ORDER
    if page == "Global · high criticality":
        return COUNTRY_ORDER
    sid = st.session_state.get("sel_site")
    row = sites[sites.site_id == sid]
    row = row if len(row) else sites.iloc[:1]
    if page == "Site compliance":
        return [row.country.iloc[0]]
    return [c for c in COUNTRY_ORDER if c in set(sites[sites.cluster == row.cluster.iloc[0]].country)]


def page_languages():
    """Translate options for the current page: the languages of the countries on screen, then English."""
    langs = []
    for c in page_countries():
        lg = COUNTRY_LANG.get(c, "en")
        if lg != "en" and lg not in langs:
            langs.append(lg)
    return [lg for lg in LANG_CHOICES if lg in langs] + ["en"]


def ui_lang():
    """Language of interface, deck and English-authored report text."""
    return lang_choice()


_MISSES = set()


def record_misses():
    return _MISSES


@st.cache_resource(show_spinner=False)
def lang_map(lang):
    """English → <lang> for every text in the app (interface, deck, reports, checklist English pivot)."""
    p = DATA / "lang" / f"{lang}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


@st.cache_resource(show_spinner=False)
def source_lang_index():
    """Checklist cell value → language of the file it came from."""
    df = load_all()[0]
    idx = {}
    for f in TRANSLATED_FIELDS:
        for v, lg in zip(df[f], df["lang"]):
            if v:
                idx.setdefault(v, lg)
    return idx


TRANSLATED_FIELDS = ["installation", "facility_type", "activity", "norm", "eu_directive", "requirement", "question",
                     "evidence", "notes", "documents", "amara_comments", "reason", "status", "criticality",
                     "frequency", "missing_document", "responsible"]


def _to(lang, en_text):
    if lang == "en" or not en_text:
        return en_text
    m = lang_map(lang)
    out = m.get(en_text) or m.get(en_text.strip())
    if out is None:
        _MISSES.add((lang, en_text))
        return en_text
    return out


def L(text):
    """Interface / deck / report text (authored in English) in the interface language."""
    if not isinstance(text, str) or not text:
        return text
    return _to(ui_lang(), text)


def english_of(text, src=None):
    """English version of a checklist cell."""
    if not isinstance(text, str) or not text:
        return text
    src = src or source_lang_index().get(text, "en")
    if src == "en":
        return text
    trmap = load_all()[1]
    return trmap.get(text) or trmap.get(text.strip()) or text


def T(text, src=None):
    """Checklist cell in the chosen language: as written when its source is in that language, otherwise English
    (checklists exist in their source language and in English)."""
    if not isinstance(text, str) or not text:
        return text
    src = src or source_lang_index().get(text, "en")
    if src == lang_choice():
        return text
    return english_of(text, src)


def shows_source(src_lang):
    """True when checklist rows of this source language appear as written."""
    return src_lang == lang_choice()


def RT(item, report_lang="en", site_lang=None):
    """Report item {'en','orig'} in the chosen language: the report's own wording when it is in that language
    (incl. checklist-language bullets inside English reports), otherwise translated from English."""
    if not isinstance(item, dict):
        return L(item)
    en, orig = item.get("en") or "", item.get("orig") or item.get("en") or ""
    lang = ui_lang()
    if lang == "en":
        return en
    if report_lang == lang:
        return orig
    if orig != en and report_lang == "en" and site_lang == lang:
        return orig
    return _to(lang, en)


def translate_df(df, cols):
    """Checklist columns in the chosen language (see T)."""
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = out[c].map(T)
    return out


def column_labels(fields):
    """Column headers in the interface language."""
    return {f: L(FIELD_LABELS_EN.get(f, f)) for f in fields}


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


def gap_panel_html(title, groups, footnote=""):
    """Grey 'Key compliance gaps' panel as used on the right of the deck slides.
    groups: [{"heading", "sub", "bullets": [{"text", "mark", "sub": [...]}]}] (deck wording, translated with L)."""
    html = f'<div class="gap-panel"><div class="gap-title">{esc(L(title))}</div>'
    for g in groups:
        h = g.get("heading", "")
        tone = "#D9822B" if "partial" in h.lower() else DSS_RED
        if h:
            html += f'<div class="gap-h" style="color:{tone}">{esc(L(h))}</div>'
        if g.get("sub"):
            html += f'<div class="gap-sub">{esc(L(g["sub"]))}</div>'
        tag = "p" if g.get("style") == "paragraph" else "li"
        items = ""
        for b in g.get("bullets", []):
            mark = f'<span class="mark">{b.get("mark")}</span> ' if b.get("mark") else ""
            sub = "".join(f"<li>{esc(L(x))}</li>" for x in b.get("sub", []))
            items += f"<{tag}>{mark}{esc(L(b['text']))}{f'<ul class=sub>{sub}</ul>' if sub else ''}</{tag}>"
        html += (items if tag == "p" else f"<ul>{items}</ul>")
    if footnote:
        html += f'<div class="gap-foot">{esc(L(footnote))}</div>'
    return html + "</div>"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))