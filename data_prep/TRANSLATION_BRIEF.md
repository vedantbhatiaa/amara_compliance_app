# Translation brief — Amara NZero H&S legal-compliance checklists

You are translating cells from occupational health & safety (H&S / OHS) legal-compliance checklists
produced by dss+ consultants for the client Amara NZero. Source languages: Spanish (Spain, Mexico,
Colombia), French, Italian, Portuguese (Portugal). Target: professional British/International English
as a compliance consultant would write it for a client report.

## Input / output
- Input file: a JSON array of objects `{"i": <int>, "lang": "<es|fr|it|pt>", "src": "<text>"}`.
- Output file: a JSON **object** mapping the index (as a string) to the English translation:
  `{"123": "English text", "124": "..."}` — one entry for EVERY `i` in the input, nothing else.
- Write the output with a short Python script (json.dump with ensure_ascii=False) rather than hand-typing
  JSON, so quotes and newlines are escaped correctly. Then re-load the file with Python and confirm the
  key count equals the input count.

## Rules
1. Translate completely and faithfully — no summarising, no omissions, no added commentary. Keep the
   same structure: line breaks (`\n`), numbering "1)", "2)", bullets, "+", "/", parentheses.
2. Do NOT translate or alter: legal citation identifiers and codes (RD 486/1997, Ley 31/1995, NOM-030-STPS-2009,
   Decreto 1072/2015, D.Lgs. 81/2008, Code du Travail Article R.4512-6, DL 50/2005, ITC-BT-05, ISO 45001,
   UNE-EN ...), IDs (ES-ACT-001), site/company names (Amara NZero, Repsol, Iberdrola, Braskem, Schneider,
   INOAC, CavyCar, Quantum, K-YENA), person names, dates, numbers, units, URLs.
3. Keep official acronyms in the original, and on first use in a cell add the English meaning in parentheses
   only when it helps a reader, e.g. "CAE (coordination of business activities)", "DUERP (single occupational
   risk assessment document)", "PAU (self-protection plan)", "OCA (authorised inspection body)",
   "REBT (Low Voltage Electrotechnical Regulation)", "RITE", "APQ", "SG-SST (OHS management system)",
   "ARL (occupational risk insurer)", "COPASST", "CSST", "DC-3", "STPS", "PDP / plan de prévention (prevention plan)",
   "preposto (supervisor)", "RSPP", "DVR (risk assessment document)", "SST". Do not expand the same acronym
   repeatedly inside one short cell.
4. Short controlled-vocabulary values must be translated consistently:
   - Compliance status: Cumplido / Cumple / Conforme / Conforme → "Compliant"; Parcial / Parcialmente cumplido /
     Parcialmente Conforme / Parzialmente Conforme → "Partially compliant"; No conforme / non conforme /
     Non conforme → "Non-compliant"; Pendiente / Pendente → "Pending"; No aplica / No se aplica / N/A /
     No relevante / Não Relevante / Non applicabile → "Not applicable".
   - Criticality: Alta/Alto/Élevée → "High"; Media/Medio/Moyenne/Média → "Medium"; Baja/Bajo/Baixa/Bassa/Faible → "Low".
   - Almacén → "Warehouse"; Oficina / Bureau / Ufficio / Escritório → "Office"; Planta industrial → "Industrial plant";
     Entrepôt → "Warehouse"; Trabajo desde Casa → "Working from home"; Domicilio trabajador → "Worker's home".
   - Column headers (e.g. "Actividad clave", "Norma / Referencia", "Requisito Legal", "Pregunta de evaluación",
     "Evidencia Requerida", "Nivel de Criticidad", "Estado de cumplimiento legal", "Razón del estado",
     "Frecuencia / Plazo legal") → "Key activity", "Standard / Reference", "Legal requirement",
     "Assessment question", "Required evidence", "Criticality level", "Legal compliance status",
     "Reason for status", "Frequency / Legal deadline".
5. Use standard English H&S terminology: evaluación de riesgos → risk assessment; vigilancia de la salud →
   health surveillance; coordinación de actividades empresariales → coordination of business activities;
   plan de autoprotección → self-protection plan; equipos de protección individual (EPI) → personal protective
   equipment (PPE); carretilla elevadora → forklift; puente grúa → overhead crane; estanterías → racking;
   atmósferas explosivas → explosive atmospheres (ATEX); boletín eléctrico → electrical installation certificate;
   muelle de carga → loading dock; puerta de carga/muelle → loading gate / dock door; consignación → lockout/tagout
   (LOTO); permiso de trabajo → work permit; simulacro → drill; brigada → emergency brigade;
   mutua / ARL → occupational risk insurer; servicio de prevención ajeno → external prevention service.
6. If a cell is already English, or is only a code/number/name, return it unchanged.
7. Spanish/Mexican informal notes and typos: translate the intended meaning into clean English.
