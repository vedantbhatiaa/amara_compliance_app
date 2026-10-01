"""Write the two dashboard workbooks to exports/ (the same files the app offers as downloads).

  exports/Amara_NZero_Legal_Compliance_Records.xlsx  complete, unfiltered records (page 1 requirements, page 2
                                                     assessed checklist, site-visit report content) — Original + English
  exports/Amara_NZero_Dashboard_Chart_Data.xlsx      one sheet per dashboard chart: its data table, totals and a native
                                                     Excel chart, plus QA reconciliation sheets

Usage:  python data_prep/export_excel.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exports import build_graph_workbook, build_records_workbook  # noqa: E402

OUT = ROOT / "exports"
OUT.mkdir(exist_ok=True)
for name, fn in [("Amara_NZero_Legal_Compliance_Records.xlsx", build_records_workbook),
                 ("Amara_NZero_Dashboard_Chart_Data.xlsx", build_graph_workbook)]:
    (OUT / name).write_bytes(fn())
    print("wrote", OUT / name)
