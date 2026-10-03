"""Assign every checklist row to a UNIQUE legal requirement (writes `req_uid` and `req_uid_type` into data/checklist.json).

Definition (owner decision, v0.6): a unique legal requirement is one legal obligation within a country. The same
obligation at several sites counts once even when each site's copy is adapted to its region (city, regional law,
regional authority) and renumbered; the same obligation for two types of business in a country (e.g. Vitoria
factory and the Spanish warehouses) also counts once in the country.

How rows are matched (requirement IDs are NOT comparable across sites — each site's copy was renumbered):
  1. Spanish warehouses (5 regionally adapted copies): the reviewed grouping in spain_warehouse_requirement_groups.json.
  2. Everywhere else: identical requirement text after removing site / city names, case, accents and punctuation
     (within a country). This also merges duplicate rows inside one checklist (e.g. France EPC lines repeated per
     piece of evidence, Valencia's six duplicated rows).
  3. Country level: groups of different types of business that share an identical requirement text are joined.
IDs: req_uid_type = <CC>-<TYPE>-<nnn> (unique within country × type of business); req_uid = <CC>-R<nnn> (country).
Usage: python data_prep/build_unique_requirements.py
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "checklist.json"
GROUPS = ROOT / "data_prep" / "spain_warehouse_requirement_groups.json"
CC = {"Spain": "ES", "Portugal": "PT", "Mexico": "MX", "Colombia": "CO", "France": "FR", "Greece": "GR", "Italy": "IT"}
TT = {"Office": "OFF", "EPC": "EPC", "Factory": "FAC", "Warehouse": "WHS", "Services": "SRV"}
SITE_ORDER = ["ES-MAD", "ES-MEC", "ES-SEV", "ES-VAL", "ES-AND", "ES-BUR", "ES-VIT", "ES-ACO", "PT-AVE", "MX-MTY",
              "MX-CDMX", "MX-INO", "MX-IBE", "MX-BRA", "MX-SCH", "MX-CHE", "MX-ALT", "CO-HOM", "CO-EPC", "FR-OFF",
              "FR-EPC", "GR-ATH", "IT-BUC"]
PLACES = (r"(madrid|meco|sevilla|seville|valencia|andoain|burgos|vitoria|a coruna|coruna|monterrey|mty|cdmx|inoac|"
          r"iberdrola|braskem|schneider|chetumal|altamira|quantum|villeurbanne|aveiro|buccinasco|athens)")


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\b(de|del|en|of|in|at|du|di|d)\s+(la\s+)?" + PLACES + r"\b", " ", t)
    t = re.sub(r"\b" + PLACES + r"\b", " ", t)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", t)).strip()


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def build():
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    order = sorted(range(len(rows)), key=lambda i: (SITE_ORDER.index(rows[i]["site_id"]), rows[i]["row"]))
    pos = {(r["site_id"], r["row"]): i for i, r in enumerate(rows)}
    # 1+2: type-level groups
    t = DSU(len(rows))
    for g in json.loads(GROUPS.read_text(encoding="utf-8"))["groups"]:
        idx = [pos[tuple(x)] for x in g]
        for i in idx[1:]:
            t.union(idx[0], i)
    first = {}
    for i in order:
        r = rows[i]
        k = (r["country"], r["business_type"], norm(r["requirement"]))
        if r["country"] == "Spain" and r["business_type"] == "Warehouse":
            continue  # reviewed grouping only
        if k in first:
            t.union(first[k], i)
        else:
            first[k] = i
    # 3: country level = type-level groups joined across types by identical text
    c = DSU(len(rows))
    for i in range(len(rows)):
        c.union(i, t.find(i))
    first = {}
    for i in order:
        k = (rows[i]["country"], norm(rows[i]["requirement"]))
        if k in first:
            c.union(first[k], i)
        else:
            first[k] = i
    # IDs in display order
    tid, cid, nt, nc = {}, {}, {}, {}
    for i in order:
        r = rows[i]
        a, b = t.find(i), c.find(i)
        if a not in tid:
            key = (r["country"], r["business_type"])
            nt[key] = nt.get(key, 0) + 1
            tid[a] = f"{CC[r['country']]}-{TT[r['business_type']]}-{nt[key]:03d}"
        if b not in cid:
            nc[r["country"]] = nc.get(r["country"], 0) + 1
            cid[b] = f"{CC[r['country']]}-R{nc[r['country']]:03d}"
        r["req_uid_type"], r["req_uid"] = tid[a], cid[b]
    DATA.write_text(json.dumps(rows, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"rows={len(rows)}  unique per country x type={len(tid)}  unique per country={len(cid)}")
    for k, v in sorted(nc.items()):
        print(f"  {k:9s} {v}")


if __name__ == "__main__":
    build()
