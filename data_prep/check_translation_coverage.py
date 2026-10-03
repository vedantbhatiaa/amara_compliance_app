"""Translation coverage + smoke test.

Runs the app (Streamlit AppTest, fresh app per state) for every site x page x every language the Translate dropdown
offers on that page, plus page 1 filtered to each country. Prints exceptions and writes to translation_misses.json
every English text that was requested in another language without a translation. Expected result: 0 exceptions and
only source-language checklist text in the misses (those are shown as written).
Usage:  python data_prep/check_translation_coverage.py
"""
import json
import os
import sys

from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app.py")
rows = json.load(open(os.path.join(ROOT, "data", "checklist.json"), encoding="utf-8"))
sites = {}
for r in rows:
    sites.setdefault(r["site_id"], (r["cluster"], r["country"]))
LANG = {"Spain": "es", "Portugal": "pt", "Mexico": "es", "Colombia": "es", "France": "fr", "Greece": "en", "Italy": "it"}
CLUSTER_LANGS = {}
for sid, (cl, co) in sites.items():
    CLUSTER_LANGS.setdefault(cl, set()).add(LANG[co])

states = []
for sid, (cl, co) in sites.items():
    base = {"sel_cluster": cl, "sel_country": co, "sel_site": sid}
    for lg in {LANG[co], "en"}:
        states.append({**base, "nav": "Site compliance", "lang_code": lg})
    for lg in CLUSTER_LANGS[cl] | {"en"}:
        states.append({**base, "nav": "Cluster results", "lang_code": lg})
for lg in ["es", "pt", "fr", "it", "en"]:
    states.append({"nav": "Global · high criticality", "lang_code": lg})
    states.append({"nav": "Legal requirements", "lang_code": lg})
for co, lg in LANG.items():
    states.append({"nav": "Legal requirements", "lang_code": lg, "r_country": [co]})

errors = 0
for st_ in states:
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in st_.items():
        if k != "lang_code":
            at.session_state[k] = v
    at.run()                                   # page opens in English (default)
    if at.session_state["lang_code"] != "en":
        errors += 1
        print("DEFAULT NOT ENGLISH", st_)
    at.session_state["lang_code"] = st_["lang_code"]
    at.run()                                   # then the language is chosen
    if at.exception:
        errors += 1
        print("EXCEPTION", st_, at.exception[0].value[:300])
    elif at.session_state["lang_code"] != st_["lang_code"]:
        errors += 1
        print("LANGUAGE NOT APPLIED", st_, at.session_state["lang_code"])
core = sys.modules["core"]
misses = sorted(core.record_misses())
F = ["installation", "facility_type", "activity", "norm", "eu_directive", "requirement", "question", "evidence", "notes",
     "documents", "amara_comments", "reason", "status", "criticality", "frequency", "missing_document", "responsible"]
src, acts = set(), set()
for r in rows:
    if r["lang"] != "en":
        src.update(r[f] for f in F if r.get(f))
        acts.add(r["activity"])
reps = json.load(open(os.path.join(ROOT, "data", "site_reports.json"), encoding="utf-8"))
for rep in reps.values():
    if rep.get("report_language") != "en":
        for ka in rep["key_activities"]:
            src.update(ka.get("regulations", []))
real = [(lg, t) for lg, t in misses if t not in src and t.split(": ")[0] not in acts]
json.dump(real, open(os.path.join(ROOT, "translation_misses.json"), "w"), ensure_ascii=False, indent=1)
print(f"states={len(states)} exceptions/language errors={errors} untranslated English texts={len(real)}")