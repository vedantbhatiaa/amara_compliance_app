"""Translation coverage + smoke test: every site x page x language mode in a fresh AppTest; prints exceptions and
lists English strings requested without a translation (written to translation_misses.json)."""
import json, sys
from streamlit.testing.v1 import AppTest
import os; APP=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app.py')
S=json.load(open(os.path.join(os.path.dirname(APP),'data','checklist.json')))
sites={}
for r in S: sites.setdefault(r['site_id'],(r['cluster'],r['country']))
PAGES=["Site compliance","Cluster results","Global · high criticality","Legal requirements"]
errs=0
def fresh(state):
    at=AppTest.from_file(APP,default_timeout=300)
    for k,v in state.items(): at.session_state[k]=v
    return at
for sid,(cl,co) in sites.items():
  for mode in ["Original","English"]:
    for p in PAGES:
        at=fresh({"lang_widget":mode,"sel_cluster":cl,"sel_country":co,"sel_site":sid,"nav":p}).run()
        if at.exception: errs+=1; print(sid,mode,p,at.exception[0].value[:300])
for co in ["Spain","Portugal","Mexico","Colombia","France","Greece","Italy"]:
    at=fresh({"lang_widget":"Original","nav":"Legal requirements","r_country_Original":[co]}).run()
    if at.exception: errs+=1; print(co,at.exception[0].value[:300])
core=sys.modules['core']
m=sorted(core.record_misses())
print("errors",errs,"misses",len(m))
json.dump(m,open('translation_misses.json','w'),ensure_ascii=False)
