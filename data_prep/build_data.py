"""Build the unified checklist dataset for the Amara NZero legal compliance app.

Reads every site checklist (Excel), maps its columns to a canonical schema,
normalises criticality and compliance status, and writes:
  app/data/checklist.json   – one record per checklist row (original language)
  build/strings.json        – every unique text value that needs an English version
"""
import json, re, unicodedata
from pathlib import Path
import openpyxl

SRC = Path("/home/claude/src")
WORK = SRC / "21dbad82-excel_working_files_without_translation/excel working files without translation"
AMZ = SRC / "Amara_NZero/05. Sent_To_Client/02. Site Visits/02. Mexico/07. Chetumal y Altamira"
OUT = Path("/home/claude/amara_compliance_app/data")
OUT.mkdir(parents=True, exist_ok=True)

# file, country, site_id, site label, business type (deck category), language, cluster
SITES = [
    (WORK/"2026_06_Checklist_Oficina_Madrid.xlsx", "Spain", "ES-MAD", "Madrid Office", "Office", "es"),
    (WORK/"2026_06_Checklist_Meco_Warehouse.xlsx", "Spain", "ES-MEC", "Meco Warehouse", "Warehouse", "es"),
    (WORK/"2026_06_Checklist_Sevilla_Warehouse.xlsx", "Spain", "ES-SEV", "Sevilla Warehouse", "Warehouse", "es"),
    (WORK/"2026_06_Checklist_Valencia_Warehouse.xlsx", "Spain", "ES-VAL", "Valencia Warehouse", "Warehouse", "es"),
    (WORK/"2026_06_Checklist_Andoain_Warehouse.xlsx", "Spain", "ES-AND", "Andoain Warehouse", "Warehouse", "es"),
    (WORK/"2026_06_Checklist_Burgos_Warehouse.xlsx", "Spain", "ES-BUR", "Burgos Warehouse", "Warehouse", "es"),
    (WORK/"2026-06_Checklist_ES_Planta_Industrial_Vitoria.xlsx", "Spain", "ES-VIT", "Vitoria Factory", "Factory", "es"),
    (WORK/"2026-06_Checklist_ACoruna_Amara_NZero_Repsol_Requisitos_legales.xlsx", "Spain", "ES-ACO", "A Coruña – Repsol in-house warehouse", "Services", "es"),
    (WORK/"2026_06_Amara_NZero_Office_Aveiro_Checklist.xlsx", "Portugal", "PT-AVE", "Aveiro Office", "Office", "pt"),
    (WORK/"2026_06_Checklist_MX_Almacen_Monterrey.xlsx", "Mexico", "MX-MTY", "Monterrey Warehouse (owned)", "Warehouse", "es"),
    (WORK/"2026_06_Checklist_Oficina_CDMX_Mexico.xlsx", "Mexico", "MX-CDMX", "CDMX Office", "Office", "es"),
    (WORK/"2026_06_Site_Visit_Report_EPC_INOAC.xlsx", "Mexico", "MX-INO", "EPC INOAC", "EPC", "es"),
    (WORK/"2026_06_Checklist_Almacen_Cliente_Mexico_Iberdrola.xlsx", "Mexico", "MX-IBE", "Iberdrola in-house warehouse", "Services", "es"),
    (WORK/"2026_06_Checklist_Almacen_Cliente Braskem_Mexico.xlsx", "Mexico", "MX-BRA", "Braskem in-house warehouse", "Services", "es"),
    (WORK/"2026_06_Site_Visit_Report_Schneider_Servicios_generales_Monterrey.xlsx", "Mexico", "MX-SCH", "Schneider general services (Monterrey)", "Services", "es"),
    (AMZ/"2026_06_Site_Visit_Report_Chetumal_Servicios_generales.xlsx", "Mexico", "MX-CHE", "Chetumal general services", "Services", "es"),
    (AMZ/"2026_06_Checklist_Almacen y servicios_Cliente_Mexico_Altamira_Quantum.xlsx", "Mexico", "MX-ALT", "Altamira – Quantum warehouse & services", "Services", "es"),
    (WORK/"2026_06_Checklist_Colombia_Teletrabajo.xlsx", "Colombia", "CO-HOM", "Home-office (teleworking)", "Office", "es"),
    (WORK/"2026_06_Colombia_EPC_Solar_Checklist_AmaraNZero.xlsx", "Colombia", "CO-EPC", "EPC Solar project", "EPC", "es"),
    (WORK/"2026_06_Checklist_Amara_NZero_France_Office_FR.xlsx", "France", "FR-OFF", "Villeurbanne Office", "Office", "fr"),
    (WORK/"2026_06_Checklist_Amara_NZero_France_EPC.xlsx", "France", "FR-EPC", "EPC – subcontractor & logistics", "EPC", "fr"),
    (WORK/"2026_06_Amara_NZero_Checklist_Greece.xlsx", "Greece", "GR-ATH", "Athens Office", "Office", "en"),
    (WORK/"2026_06_Checklist_IT_Office_Buccinasco.xlsx", "Italy", "IT-BUC", "Buccinasco Office (HQ)", "Office", "it"),
]
CLUSTER = {"Spain": "Spain & Portugal", "Portugal": "Spain & Portugal", "Mexico": "Mexico & Colombia",
           "Colombia": "Mexico & Colombia", "France": "France", "Greece": "Greece & Italy", "Italy": "Greece & Italy"}

def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()

# canonical field -> predicate on normalised header (order matters: first match wins per field)
FIELD_RULES = [
    ("id", lambda h: h == "id"),
    ("facility_type", lambda h: h.startswith(("tipo de instal", "type d'instal", "facility type", "tipo di instal"))),
    ("installation", lambda h: h.startswith(("instal", "facility", "installazione"))),
    ("activity", lambda h: h.startswith(("actividad clave", "activite cle", "key activity", "atividade-chave", "attivita chiave"))),
    ("norm", lambda h: h.startswith(("norma / r", "norme / r", "standard / ref"))),
    ("eu_directive", lambda h: h.startswith(("directiva", "eu directive", "diretiva", "direttiva"))),
    ("requirement", lambda h: h.startswith(("requisito legal", "exigence legale", "legal requirement"))),
    ("question", lambda h: h.startswith(("pregunta", "question", "pergunta", "domanda", "evaluation question"))),
    ("evidence", lambda h: h.startswith(("evidencia", "preuve", "required evidence", "evidencia requerida", "evidenza"))),
    ("criticality_aa", lambda h: h.startswith("niveau de criticite aa")),
    ("criticality", lambda h: ("criticid" in h or "criticit" in h or "criticality" in h)),
    ("notes", lambda h: h in ("notas", "notes")),
    ("documents", lambda h: h.startswith("documentos o cert")),
    ("amara_comments", lambda h: h.startswith(("comentarios amara", "comentarios equipo amara", "observaciones amara"))),
    ("reason", lambda h: h.startswith(("razon", "raison", "reason", "motivo"))),
    ("status", lambda h: h.startswith(("estado", "nuevo estado", "statut", "state of legal", "stato di conform"))),
    ("comments", lambda h: h == "comentarios"),
    ("responsible", lambda h: h.startswith("respons")),
    ("frequency", lambda h: h.startswith(("frecuencia", "frequence", "frequency", "frequencia", "frequenza"))),
    ("missing_document", lambda h: h.startswith("missing document")),
]

def map_headers(headers):
    m = {}
    for idx, h in enumerate(headers):
        hn = norm(h)
        if not hn:
            continue
        for field, pred in FIELD_RULES:
            if field not in m and pred(hn):
                m[field] = idx
                break
    return m

def crit_norm(v):
    s = norm(v)
    if s.startswith(("alt", "high", "elev")): return "High"
    if s.startswith(("medi", "moyen")): return "Medium"
    if s.startswith(("baj", "baix", "bass", "faib", "low")): return "Low"
    return "Not rated"

def status_norm(v, fill=None):
    s = norm(v)
    if not s or s == "none":
        if fill:  # France: status encoded as cell colour
            f = fill.upper()
            if f.endswith("FF0000") or f.endswith("C00000"): return "Non-compliant"
            if f.endswith("FFC000") or f.endswith("FFFF00"): return "Partially compliant"
            if f.endswith("00B050") or f.endswith("92D050"): return "Compliant"
        return "Not assessed"
    if s.startswith(("parcial", "partial", "parzial")): return "Partially compliant"
    if s.startswith(("no conforme", "non conforme", "no cumpl", "no compliance", "non-compl", "non compl")): return "Non-compliant"
    if s.startswith(("pendiente", "pendente", "pending")): return "Non-compliant"
    if s.startswith(("no aplica", "no se aplica", "n/a", "no relevante", "nao relevante", "not relevant", "non applicabile")):
        return "Not applicable"
    if s.startswith(("cumpl", "conforme", "cumple", "full", "fully")): return "Compliant"
    return "Not assessed"

records, header_labels = [], {}
for path, country, site_id, site, btype, lang in SITES:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = next(w for w in wb.worksheets if not norm(w.title).startswith(("leyenda", "legend", "legenda", "step", "ejemplo")))
    hdr_row = next(r for r in range(1, 20) if any(norm(ws.cell(r, c).value) == "id" for c in range(1, 4)))
    headers = [ws.cell(hdr_row, c).value for c in range(1, ws.max_column + 1)]
    cmap = map_headers(headers)
    if "criticality_aa" in cmap:          # France office: use the reviewed (AA) criticality column
        cmap["criticality_orig"] = cmap["criticality"]; cmap["criticality"] = cmap.pop("criticality_aa")
    if "reason" not in cmap and "comments" in cmap:
        cmap["reason"] = cmap.pop("comments")
    header_labels[site_id] = {f: str(headers[i]).strip() for f, i in cmap.items()}
    blanks, n = 0, 0
    for r in range(hdr_row + 1, ws.max_row + 1):
        rid = ws.cell(r, 1).value
        has_id = bool(rid and str(rid).strip())
        # QA fix (v0.3): some checklists (Iberdrola, Braskem, Altamira) list assessed requirements with an empty
        # ID cell. Keep any row that has content in the requirement columns, not only rows with an ID.
        has_content = any(ws.cell(r, c).value not in (None, "") for c in range(2, 8))
        if not has_id and not has_content:
            blanks += 1
            if blanks > 40: break
            continue
        blanks = 0
        rec = {"country": country, "cluster": CLUSTER[country], "site_id": site_id, "site": site,
               "business_type": btype, "lang": lang, "row": r, "id_missing": not has_id}
        for f, i in cmap.items():
            v = ws.cell(r, i + 1).value
            if hasattr(v, "strftime"): v = v.strftime("%Y-%m-%d")
            rec[f] = (str(v).strip() if v is not None else "")
        st_cell = ws.cell(r, cmap["status"] + 1) if "status" in cmap else None
        fill = st_cell.fill.fgColor.rgb if (st_cell is not None and st_cell.fill and st_cell.fill.fill_type and isinstance(st_cell.fill.fgColor.rgb, str)) else None
        rec["criticality_level"] = crit_norm(rec.get("criticality"))
        rec["status_level"] = status_norm(rec.get("status"), fill)
        rec["status_from_colour"] = bool(not rec.get("status") and rec["status_level"] != "Not assessed")
        # status read from the cell colour when the status cell is empty (France checklists, one Burgos row)
        rec["status_source"] = "text" if rec.get("status") else ("cell colour" if rec["status_level"] != "Not assessed" else "empty")
        records.append(rec); n += 1
    print(f"{site_id:8s} {n:4d} rows  fields={sorted(cmap)}")

TEXT_FIELDS = ["installation", "facility_type", "activity", "norm", "eu_directive", "requirement", "question",
               "evidence", "notes", "documents", "amara_comments", "reason", "status", "criticality", "frequency",
               "missing_document", "responsible", "criticality_orig"]
strings = {}
for rec in records:
    if rec["lang"] == "en":
        continue
    for f in TEXT_FIELDS:
        v = rec.get(f)
        if v and re.search(r"[A-Za-zÀ-ÿ]{3,}", v):
            strings.setdefault(v, rec["lang"])
for sid, labels in header_labels.items():
    lang = next(s[5] for s in SITES if s[2] == sid)
    if lang != "en":
        for v in labels.values(): strings.setdefault(v, lang)

json.dump(records, open(OUT / "checklist.json", "w"), ensure_ascii=False, indent=0)
json.dump(header_labels, open(OUT / "header_labels.json", "w"), ensure_ascii=False, indent=1)
Path("/home/claude/build").mkdir(exist_ok=True)
json.dump(strings, open("/home/claude/build/strings.json", "w"), ensure_ascii=False, indent=0)
print("records", len(records), "strings", len(strings), "chars", sum(map(len, strings)))
