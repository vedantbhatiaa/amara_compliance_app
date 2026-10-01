"""Officially reported chart figures and key-gap text, transcribed from the dss+ June 2026 decks.
Counts are [compliant, partially compliant, non-compliant] per criticality level."""
import json

S = lambda h, m, l: {"High": h, "Medium": m, "Low": l}

site_figures = {  # cluster presentations, "Compliance Status by Criticality: <site>"
    "ES-VIT": S([2, 15, 9], [1, 16, 1], [0, 1, 1]),
    "ES-SEV": S([20, 8, 7], [4, 11, 4], [0, 0, 0]),
    "ES-MEC": S([16, 2, 14], [8, 11, 7], [0, 1, 4]),
    "ES-VAL": S([16, 3, 6], [8, 16, 3], [1, 9, 0]),
    "ES-AND": S([1, 16, 4], [1, 8, 15], [0, 1, 3]),
    "ES-BUR": S([9, 6, 2], [2, 18, 1], [0, 11, 0]),
    "ES-ACO": S([8, 0, 0], [2, 1, 0], [0, 0, 0]),
    "ES-MAD": S([8, 1, 0], [0, 9, 6], [3, 1, 0]),
    "PT-AVE": S([4, 3, 1], [11, 4, 4], [2, 7, 1]),
    "MX-MTY": S([23, 7, 5], [22, 6, 0], [8, 0, 1]),
    "MX-INO": S([13, 0, 3], [7, 2, 3], [7, 1, 0]),
    "MX-CDMX": S([22, 1, 2], [7, 3, 1], [6, 1, 0]),
    "CO-HOM": S([3, 1, 1], [1, 1, 2], [1, 2, 9]),
    "CO-EPC": S([6, 0, 10], [3, 4, 12], [1, 2, 1]),
    "FR-OFF": S([0, 0, 3], [0, 0, 5], [0, 0, 10]),
    "FR-EPC": S([0, 1, 5], [0, 0, 4], [0, 0, 3]),
    "GR-ATH": S([4, 0, 3], [4, 1, 3], [1, 0, 2]),
    "IT-BUC": S([11, 2, 0], [14, 2, 1], [3, 4, 0]),
}
# Mexico in-house services are reported as one aggregate slide (Iberdrola + Schneider + Braskem)
group_figures = {"MX-SERVICES": {"label": "Mexico in-house services (Iberdrola, Schneider, Braskem)",
                                 "sites": ["MX-IBE", "MX-SCH", "MX-BRA"],
                                 "figures": S([16, 7, 13], [17, 4, 9], [7, 6, 4])}}

cluster_figures = {  # global deck pp.14-19 "Compliance Status per criticality of business in the <cluster>"
    "Spain & Portugal": {
        "Office": S([12, 3, 2], [11, 13, 10], [5, 8, 1]),
        "Factory": S([2, 15, 9], [1, 16, 1], [0, 1, 1]),
        "Warehouse": S([62, 35, 33], [23, 64, 30], [1, 22, 7]),
        "Services": S([10, 0, 0], [0, 1, 0], [0, 0, 0]),
    },
    "Mexico & Colombia": {
        "Office": S([25, 2, 3], [8, 4, 3], [7, 3, 9]),
        "EPC": S([19, 0, 13], [11, 5, 15], [8, 3, 1]),
        "Warehouse": S([23, 7, 5], [22, 6, 0], [8, 0, 1]),
        "Services": S([16, 7, 13], [17, 4, 9], [7, 6, 4]),
    },
    "France": {
        "Office": S([0, 0, 3], [0, 0, 5], [0, 0, 10]),
        "EPC": S([0, 1, 5], [0, 0, 4], [0, 0, 3]),
    },
    "Greece & Italy": {
        "Office": S([15, 2, 3], [18, 3, 3], [4, 5, 2]),
    },
}

# global deck pp.12-13 "Compliance Status by High Criticality per type of business in the different clusters"
global_high = [
    {"business_type": "Office", "cluster": "France", "flags": ["FR"], "values": [0, 0, 3]},
    {"business_type": "Office", "cluster": "Greece & Italy", "flags": ["GR", "IT"], "values": [15, 2, 3]},
    {"business_type": "Office", "cluster": "Mexico & Colombia", "flags": ["MX", "CO"], "values": [25, 2, 3]},
    {"business_type": "Office", "cluster": "Spain & Portugal", "flags": ["ES", "PT"], "values": [12, 3, 2]},
    {"business_type": "EPC", "cluster": "France", "flags": ["FR"], "values": [0, 1, 5]},
    {"business_type": "EPC", "cluster": "Mexico & Colombia", "flags": ["MX", "CO"], "values": [19, 0, 13]},
    {"business_type": "Factory", "cluster": "Spain & Portugal", "flags": ["ES"], "values": [2, 15, 9]},
    {"business_type": "Warehouse", "cluster": "Mexico & Colombia", "flags": ["MX"], "values": [23, 7, 5]},
    {"business_type": "Warehouse", "cluster": "Spain & Portugal", "flags": ["ES"], "values": [62, 35, 33]},
    {"business_type": "Services", "cluster": "Mexico & Colombia", "flags": ["MX"], "values": [16, 7, 13]},
    {"business_type": "Services", "cluster": "Spain & Portugal", "flags": ["ES"], "values": [10, 0, 0]},
]

site_gaps = {
 "FR-OFF": [("High criticality – not compliant", ["Single Document for Occupational Risk Assessment (DUERP)",
    "Fire equipment certification, evacuation marshal designation, posted safety/evacuation instructions",
    "Defibrillator presence and validity check"]),
   ("Medium criticality – not compliant", ["A documented psychosocial risk assessment covering office-related psychosocial hazards.",
    "A psychosocial action plan, including corrective actions, responsibilities, deadlines, and employee training (including harassment awareness).",
    "A formalized emergency plan that is communicated to all employees.",
    "Up-to-date emergency preparedness, including trained first aid personnel (SST), current emergency procedures, and valid SST cards."])],
 "FR-EPC": [("High criticality – not compliant", ["Service contract", "Prevention plan including a risk analysis review at project launch",
    "Safety Data Sheet (SDS)", "Insurance contract", "Formalized emergency plan and emergency measures"]),
   ("Medium criticality – not compliant", ["Valid tax and URSSAF compliance certificates for all subcontractors.",
    "Evidence of workers' qualifications, certifications, and authorizations (e.g., CACES, electrical authorization, SST).",
    "Records verifying the availability and adequacy of PPE and collective protective equipment throughout the project.",
    "Valid insurance certificates for all subcontractors."])],
 "GR-ATH": [("High criticality – not compliant", ["Risk assessment document of the office",
    "Training & Drills: evacuation drill log and training log and certificates of employees",
    "Safety Technician assignment and related documents (Safety Technician suggestions, records of submitted SEPE notifications, accident logbook)"]),
   ("Medium criticality – not compliant", ["Fire safety: documented fire study and responsible person designated",
    "Internal accidents logbook", "Signed OSH policy document", "Written telework agreements per employee"])],
 "IT-BUC": [("High criticality – not compliant", ["Mandatory periodic inspection of the grounding (earthing) system",
    "Supervisor (preposto) safety training to 12 hours as required"]),
   ("Medium criticality – not compliant", ["Six-monthly extinguisher maintenance records",
    "Emergency numbers posted as standalone visible notice and first aid kit complete and compliant",
    "Legionella risk assessment (Circular Min. Health 2015 / ISS Guidelines 2015) + water system control and maintenance plan + sampling records (if applicable)"])],
 "MX-MTY": [("High criticality – not compliant", ["Emergency drill records: date, scenario, participants, evacuation time, findings, and corrective actions",
    "Contractor management: risk information delivered to contractors is missing with signed acknowledgment, pre-qualification checklist, HSE contract clause, signed induction records prior to first access, work permit model and logs.",
    "Forklift and equipment: defect and repair records",
    "Fire risk and prevention: assessment, calculation evidence, mandatory controls determination, corrective action records, and last review date",
    "Evacuation routes and emergency lighting: evacuation route plan, monthly inspection records of routes and signage, and emergency lighting test records"])],
 "MX-INO": [("High criticality – not compliant", ["Contractor evaluation: pre-qualification records per subcontractor, signed H&S obligations in subcontracts, and monthly H&S performance supervision evidence",
    "Site access control and registers are missing",
    "Incident reporting: reporting procedure, investigation reports, lessons learned communications, and corrective action records with closure dates"])],
 "MX-IBE": [("Iberdrola (warehouse) – key gaps", ["Risk assessments documentation for crane and forklift activities and critical operations records",
    "Hazardous materials training of employees", "Fire risk classification and control", "HSE contract annexes are missing",
    "DC-3s for crane, forklift, and critical operators; equipment certifications and periodic inspection records",
    "Approved load limits, racking types, lifting and load risk assessments, site layout, risk maps, and area demarcation",
    "Traffic signage, safe pedestrian walkways, loose load securing, and operational procedures",
    "Labeling on chemical containers, safe lubricant storage, and proper grounding in chemical storage area",
    "Emergency response plan aligned with Iberdrola's, brigade training, fire suppression system reviews and drill planning"])],
 "MX-SCH": [("Schneider (general services) – key gaps", ["Risk assessment documentation and records",
    "Training program evidence and DC-3s where applicable",
    "Worker awareness records for risk assessments, site layout, risk zone maps, hazmat and critical operations training, and area demarcation verification"])],
 "MX-BRA": [("Braskem (warehouse) – key gaps", ["Hazmat safety information for temporary materials on site",
    "Risk assessments and critical operations records maintained since start of operations, and flammable materials storage risk evaluation"])],
 "MX-CDMX": [("High criticality – not compliant", ["Evacuation drills: pending joint evacuation drill evidence with rest of building occupants",
    "Emergency routes: missing safety signs on emergency routes",
    "Electrical installations: live electrical risks, power strips pending approval, loose cables in corridor, microwave wiring pending load verification"]),
   ("Medium criticality – not compliant", ["SST documentary control index + sample of retained documents with dates and signature",
    "Contractors & visitors: missing security induction at entry",
    "Emergency brigades: missing evidence of brigade integration with the building"])],
 "CO-HOM": [("High criticality – not compliant", ["Accident reporting and ARL: home accident reporting procedure and ARL affiliation certificates for all Colombian workers",
    "Workplace Coexistence Committee (CCL): constitution act, worker communication, and accessible reporting channel for remote workers"]),
   ("Medium criticality – not compliant", ["Home office risk information: risk disclosure document and signed acknowledgment records for all Colombian workers",
    "Psychosocial risk: assessment not applied, missing results, and intervention plan",
    "Home emergency protocol: procedure, signed acknowledgments, and emergency directory"])],
 "CO-EPC": [("High criticality – not compliant", ["Contractor management: HSE Coordinator credentials, meeting minutes, HSE inspections, corrective action plans, activity suspension records, signed induction records, and solar site-specific induction content.",
    "Lifting equipment: plans, operator competency certificates, pre-operational and technical inspection records, certificates (crane, hoist, slings).",
    "Working at height: fall prevention program, valid certificates (max. 3 years) for all workers including contractors, PTWs, coordinator certification and appointment, height PPE, anchor point certificates and inspections.",
    "Electrical workers: valid licenses, CONTE verification (National Council of Electrical Technicians), authorized worker list, and defined roles per technician.",
    "LOTO: photovoltaic procedure (DC/AC), application records, calibrated voltage verification equipment, and training records.",
    "Dual-risk activities (electrical + height): safe work procedures, dielectric and fall arrest PPE compatibility verification, and CTTA/RETIE dual authorization."])],
 "ES-VIT": [("High criticality – not compliant", ["Business opening license: classified activity license or equivalent environmental authorization not yet obtained",
    "Explosive atmosphere zones (ATEX): explosive atmosphere risk assessment considering ignition probability and zone classification not completed",
    "Contractor management: 1) operational CAE platform; 2) verified contractor OHS documentation (risk assessment, planning, training, medical fitness, insurance); 3) work-permit control procedure.",
    "Loading gate: 1) certificate of the loading-gate safety devices; 2) six-monthly maintenance records by an authorized company; 3) result of the functional verification; 4) preventive maintenance plan for all loading gates; 5) dated and signed intervention records by an authorized company."]),
   ("High criticality – partially compliant", ["Loading and unloading: 1) training record for packing/unpacking jobs; 2) CE marking and declarations of conformity of packing equipment (strapping, winding, wrapping machines); 3) equipment inventory with guard status; 4) manuals accessible at the workstation.",
    "Technical installation: 1) low-voltage and high-voltage electrical installation certification and periodic inspection missing; 2) inventory of pressure equipment",
    "Machinery compliance: machinery must 1) carry CE marking, 2) declaration of conformity, 3) regular OCA inspections, 4) maintenance records"])],
 "ES-SEV": [("High criticality – not compliant", ["Lifting equipment use: missing 1) a documented safe lifting and suspended-load handling procedure, including controls to prevent personnel from passing beneath suspended loads, and 2) documented monthly racking inspection records and a procedure for the immediate removal or isolation of damaged rack bays.",
    "Loading gate: missing 1) a documented maintenance plan for manual loading doors and 2) a loading/unloading procedure requiring the use of wheel chocks, including compliance monitoring records.",
    "Falling objects: missing 1) documented monthly racking inspection records, 2) a procedure for the immediate withdrawal and repair of damaged rack bays, 3) documented pre-use inspection records for lifting hooks and safety brakes, 4) an up-to-date lifting accessories inventory with a defective-equipment disposal procedure and records, and 5) training records on safe palletizing and material storage to prevent falling-object hazards.",
    "Contractor management: missing 1) a documented contractor management and verification procedure, 2) records of contractor compliance checks through the CAE platform, 3) on-site contractor supervision and inspection records, and 4) evidence that contractors meet all applicable legal and site-specific safety requirements before and during work execution."]),
   ("High criticality – partially compliant", ["Loading/unloading: missing 1) an updated manual material handling (MMH) risk assessment with a documented action plan, and 2) records of periodic verification of machinery safeguards and mandatory PPE use during loading/unloading operations."])],
 "ES-MEC": [("High criticality – not compliant", ["Manual handling: missing 1) manual handling risk assessment using a recognized methodology, 2) assessment of high-risk lithium battery handling tasks, and 3) occupational health surveillance records demonstrating investigation, follow-up, and corrective actions related to reported musculoskeletal complaints.",
    "Machinery guarding: missing 1) evidence that maintenance contractors have documented LOTO procedures for machinery and industrial doors, 2) verification that these procedures are implemented during maintenance activities, and 3) contractor competence/training records related to hazardous energy control and entrapment prevention.",
    "Contractor management: missing 1) a formal contractor induction/work authorization process covering task and site-specific risk review, required PPE, and equipment/tools verification, 2) documented communication to affected site personnel regarding contractor activities, 3) identification of situations requiring preventive resources or special controls (e.g., ATEX areas), and 4) records demonstrating contractor compliance with these requirements during work execution.",
    "Loading and unloading: missing 1) documented controls to prevent trailer movement during loading/unloading (preferably a mechanical restraint system), 2) inspection records confirming correct wheel chock use (quantity, size, and positioning), 3) a formal vehicle key control procedure during loading/unloading operations, and 4) evidence of implementation and monitoring of these controls following previous incidents/near misses."]),
   ("High criticality – partially compliant", ["Fire safety: 1) justification for exemption from a Fire Safety Self-Protection Plan and 2) fire emergency training records for designated personnel are needed."])],
 "ES-VAL": [("High criticality – not compliant", ["Fire risk: 1) intrinsic fire-risk level not determined (fire-load calculation per RSCIEI Annex I missing); OCA inspection frequency and Self-Protection Plan requirement unknown. 2) Self-Protection Plan not elaborated, implemented or registered with the Generalitat Valenciana despite likely obligation given warehouse size.",
    "Contractor management: 1) no effective CAE control, neither via platform nor on-site; area team unaware of contractors/subcontractors working in their zone. 2) No written risk-information delivery with signed acknowledgement per contractor before work commences. 3) No work-authorisation process covering task-specific risk review, PPE verification, and equipment/tools check per contractor intervention. 4) No documented communication to site personnel about contractor activities."]),
   ("High criticality – partially compliant", ["Fire risk: missing 1) intrinsic fire-risk level calculation (fire-load per RSCIEI Annex I), required to determine OCA inspection frequency and whether a Self-Protection Plan is mandatory, 2) OCA corrective-action status from 2025 inspection not yet documented, 3) evacuation routes partially obstructed and emergency-lighting test records absent."])],
 "ES-AND": [("High criticality – not compliant", ["Loading gates: missing 1) loading gate safety certification and anti-entrapment device inspection records, 2) a preventive maintenance plan and maintenance/intervention records for loading doors, 3) a documented dock operation procedure, including wheel chock management and bay occupancy controls, and 4) evidence of fall protection measures at loading docks.",
    "Explosive atmosphere zones: missing 1) an ATEX risk assessment and Explosion Protection Document (EPD/DPCE), 2) an ATEX zone classification plan prepared by a competent person, 3) ATEX training records and a list of authorized personnel by zone, 4) certified antistatic PPE documentation and issuance records, and 5) an ATEX work permit system and designation of preventive resources where required.",
    "Contractor management: missing 1) documented CAE coordination and information exchange with all contractors and concurrent employers, 2) systematic contractor document verification records (e.g., through a CAE platform), 3) written designation of preventive resources for high-risk activities, and 4) a work permit system for contractors performing high-risk work.",
    "Hazardous substances inventory: missing 1) a complete chemical inventory with verified and accessible Safety Data Sheets (SDSs), 2) a chemical exposure assessment and industrial hygiene monitoring reports, 3) an inventory of carcinogenic/mutagenic agents and individual exposure records, 4) ventilation verification/certification records for chemical handling areas, and 5) hazardous waste management records, including waste registers, acceptance forms, and contracts with authorized waste contractors."])],
 "ES-BUR": [("High criticality – not compliant", ["Loading and unloading: missing 1) a loading/unloading risk assessment covering forklift and overhead crane operations, including poorly secured loads, and 2) a documented preventive action plan addressing the risks and improvement opportunities identified in the assessment."]),
   ("High criticality – partially compliant", ["Load at height: missing 1) a storage and racking risk assessment in accordance with RD 486/1997 and applicable technical guidance (NTPs), and 2) a documented storage allocation procedure defining the permitted rack locations based on transformer weight and rack load capacity, with resulting actions incorporated into the preventive action plan.",
    "Industrial vehicles: missing 1) a risk assessment for forklifts and pallet trucks, including traffic routes and operating surface conditions, 2) CE compliance documentation, instruction manuals, maintenance plans and inspection records, 3) operator training and training records, and 4) evidence of effective implementation and follow-up of pre-use forklift inspection checklists."])],
 "ES-ACO": [("Medium criticality – partially compliant", ["Explosive atmosphere zone verification: verification of the client's explosive atmosphere zone classification document prior to worker deployment is missing."])],
 "ES-MAD": [("High criticality – partially compliant", ["Electrical installation: missing the current REBT Electrical Installation Certificate (Boletín), including any certificates issued following substantial modifications."])],
 "PT-AVE": [("High criticality – not compliant", ["Health & safety training: specific occupational health and safety training tailored to the role and identified risks not conducted or formally documented",
    "Evacuation and exit signage: exit signs and evacuation route markings not fully in place or not compliant with requirements",
    "Emergency plan: internal emergency plan not fully developed or not formally approved",
    "First aid provision: adequate first aid equipment and trained personnel not fully ensured relative to workforce size and identified risks"])],
}

cluster_gaps = {
 "Spain & Portugal": [
  ("Warehouse", ["Contractor management is the most pervasive weakness, with non-conformities at every site except Burgos: no formal contractor verification and work-authorization process, ineffective use of the CAE platform, insufficient on-site supervision, and no documented communication to site personnel on contractor activities and special-control areas.",
   "Loading and unloading operations show consistent gaps across Sevilla, Meco, Andoain and Burgos, principally around trailer/wheel restraint controls, dock maintenance and operation procedures, and supporting risk assessments.",
   "Storage and falling-object controls (racking inspections and damaged-bay removal) are deficient at Sevilla; manual handling and machinery safety gaps (lithium-battery handling, health surveillance, contractor LOTO) are concentrated at Meco.",
   "Fire safety is a high-priority regulatory exposure at Valencia: intrinsic fire-risk level not determined and the legally required Self-Protection Plan not prepared or registered.",
   "Hazardous-substances management at Andoain lacks a complete chemical inventory, exposure and hygiene monitoring, carcinogen/mutagen controls, ventilation certification and waste-management records.",
   "ATEX management is a significant concern at Andoain: risk assessments, Explosion Protection Documents (EPD/DPCE), zone classification, training, authorized-personnel lists and certified PPE documentation are incomplete or missing."]),
  ("Factory", ["ATEX zones: explosive atmosphere risk assessment (ignition probability and zone classification) not completed.",
   "Contractor management: missing operational CAE platform, verified contractor OHS documentation (risk assessment, planning, training, medical fitness, insurance), and a work-permit control procedure.",
   "Loading gate: missing safety-device certificate, six-monthly maintenance records by an authorized company, functional verification results, preventive maintenance plan for all gates, and dated/signed intervention records.",
   "Loading and unloading: missing training records for packing/unpacking jobs, CE marking and declarations of conformity for packing equipment, equipment inventory with guard status, and manuals at the workstation.",
   "Technical installation: missing low- and high-voltage electrical installation certification and periodic inspection, and a pressure-equipment inventory.",
   "Machinery compliance: machinery missing CE marking, declaration of conformity, regular OCA inspections, and maintenance records."]),
  ("Office", ["Aveiro lacks emergency preparedness (emergency plan, evacuation signage, first aid) and role-specific OHS training.",
   "Madrid's only high-criticality gap is the missing current REBT Electrical Installation Certificate (Boletín)."]),
  ("Services", ["Spain (Repsol A Coruña in-house warehouse): no critical compliance gaps identified; one medium-criticality partial item on verification of the client's ATEX zone classification."]),
 ],
 "Mexico & Colombia": [
  ("Warehouse", ["Owned warehouse (Monterrey): a few items remain missing – emergency drill records, contractor management documents (risk acknowledgment, pre-qualification, HSE clause, inductions, work permits), and fire risk and prevention evidence."]),
  ("Services", ["Braskem (in-house warehouse): missing risk assessment documentation, including critical operations records since the start of operations and the flammable materials storage risk evaluation.",
   "Schneider (in-house general services): missing risk assessment documentation and records, training programme evidence and DC-3s, risk zone maps, hazmat and critical operations training, and area demarcation verification.",
   "Iberdrola (in-house warehouse): documentation (crane/forklift and critical operations risk assessments); training & certifications (hazmat training, DC-3s, equipment certifications and inspection records); site organisation (load limits, racking, layout, risk maps, demarcation, signage, walkways, load securing, procedures); chemical safety (labelling, lubricant storage, grounding); fire & emergency (fire risk classification, emergency plan aligned with Iberdrola's, brigade training, fire suppression reviews, drills)."]),
  ("EPC", ["Mexico shows legal compliance gaps in 1) subcontracting HSE clauses, 2) access control and 3) incident investigation.",
   "Colombia – contractor management: HSE Coordinator credentials, meeting minutes, HSE inspections, corrective action plans, activity suspension records, signed induction records and solar site-specific induction content.",
   "Colombia – lifting equipment: plans, operator competency certificates, pre-operational and technical inspection records, certificates (crane, hoist, slings).",
   "Colombia – LOTO: photovoltaic procedure (DC/AC), application records, calibrated voltage verification equipment and training records."]),
  ("Office", ["Colombia: the Labor Coexistence Committee (CCL) has not been established and the notification of the home-based work arrangement to the ARL (occupational risk insurer) is missing.",
   "CDMX office: pending joint evacuation drill evidence with other building occupants, missing safety signage on emergency routes, and electrical issues (live risks, unapproved power strips, loose corridor cables, pending microwave wiring load verification)."]),
 ],
 "France": [
  ("EPC", ["Service contract", "Prevention plan including a risk analysis review at project launch", "Safety Data Sheet (SDS)",
           "Insurance contract", "Formalized emergency plan and emergency measures"]),
  ("Office", ["Single Document for Occupational Risk Assessment (DUERP)",
              "Fire equipment certification, evacuation marshal designation, posted safety/evacuation instructions",
              "Defibrillator presence and validity check"]),
 ],
 "Greece & Italy": [
  ("Office – Greece", ["Risk assessment document of the office",
    "Training & Drills: evacuation drill log, training log and certificates of employees",
    "Safety Technician assignment and related documents (Safety Technician suggestions, records of submitted SEPE notifications, accident logbook)"]),
  ("Office – Italy", ["Supervisor (preposto) safety training to 12 hours as legally required",
    "Mandatory periodic inspection of the grounding (earthing) system"]),
 ],
}

global_gaps = [
 ("Warehouses", ["Spain – contractor management (all sites except Burgos): no formal verification/work-authorization process, ineffective CAE platform use, insufficient supervision, poor communication to site personnel.",
   "Spain – loading and unloading (Sevilla, Meco, Andoain, Burgos): gaps in trailer/wheel restraints, dock procedures and risk assessments.",
   "Spain – storage and manual handling: deficient racking inspections at Sevilla; manual handling and machinery gaps at Meco (lithium-battery handling, health surveillance, contractor LOTO).",
   "Spain – fire safety (Valencia): fire-risk level not determined and Self-Protection Plan not prepared or registered.",
   "Spain – hazardous substances and ATEX (Andoain): missing chemical inventory, exposure/hygiene monitoring, carcinogen controls, ventilation certification, waste records; incomplete ATEX risk assessments, EPD/DPCE, zone classification, training and certified PPE.",
   "Mexico MTY: emergency drill records, contractor management documents (risk acknowledgment, pre-qualification, HSE clause, inductions, work permits) and fire risk and prevention evidence remain missing."]),
 ("EPC", ["Mexico: gaps in subcontracting HSE clauses, access control and incident investigation.",
   "France: lacks several key documents (service contract, prevention plan with launch risk analysis, Safety Data Sheets, insurance contract, formalized emergency plan).",
   "Colombia: significant gaps in contractor management, lifting equipment and LOTO documentation."]),
 ("Factory", ["Critical compliance gaps across ATEX zones, contractor management, the loading gate, loading and unloading operations, technical installations and machinery compliance – incomplete explosive-atmosphere risk assessments, missing contractor verification and work-permit controls, absent gate and machinery certifications and inspections, and unavailable electrical and pressure-equipment documentation."]),
 ("Services", ["Mexico: all three in-house sites lack core documentation – Braskem (critical operations records since start-up and flammable storage evaluation), Schneider (risk assessments, training/DC-3s, risk zone maps, hazmat and critical-ops training, area demarcation) and Iberdrola (crane/forklift assessments, hazmat training, operator DC-3s and equipment certifications, site organisation, chemical safety, fire/emergency plans).",
   "Spain: no critical compliance gaps were identified."]),
 ("Offices", ["France is missing its occupational risk assessment (DUERP), fire equipment certification, evacuation marshal designation, posted safety instructions and defibrillator check.",
   "Greece lacks its office risk assessment, training and evacuation drill records, and Safety Technician assignment documents.",
   "Italy has gaps in the legally required supervisor (preposto) safety training and the mandatory grounding-system inspection."]),
]

exec_summary = {
 "strengths": ["184 compliant critical regulatory items",
   "ISO 45001 certification achieved at all sites in Spain (Meco, Sevilla, Valencia, Burgos, Madrid…) except CavyCar's, and ISO 9001, 14001 and 45001 certifications in place in Mexico through an Integrated Management System (SGI)",
   "H&S management system in developing stages (starting to report H&S metrics, risk assessment processes and controls in few critical operations, annual internal inspections, annual safety meetings…) and partially compliant with local legislation",
   "EHS technical experience within the team of Spain – outsourced in several countries (Greece, Italy, Portugal)",
   "Industrial operations show different levels of safety maturity; in general, positive leadership engagement in some countries and operations – depending on individual commitment rather than corporate standard",
   "Offices in good physical conditions in several countries (Spain, Italy, Mexico, France…) – safety depends on landlord company practices"],
 "gaps": ["161 critical gaps (89 non-compliant and 72 partially compliant)",
   "Non-homogeneous leadership commitment with safety and non-risk prevention focus – unmanaged site-specific operational risks",
   "Focus on regulatory compliance – safety tends to be treated as a bureaucratic target rather than a genuine priority",
   "Safety culture remains predominantly reactive – actions driven by urgency rather than prevention",
   "Lack of clear H&S organisation across geographies – no H&S dedicated resources or H&S competency (internal or external) in specific geographies",
   "No formal and recurrent safety culture training – only legally required",
   "At the factory, significant gaps were identified, several requiring immediate action",
   "Employee commitment to safety appears markedly stronger at client-operated warehouses than at Amara NZero's own facilities",
   "H&S practices with contractors need strengthening across EPC and other activities – contracting process requires stronger initial risk assessment and resource planning"],
}

cluster_meta = {
 "Spain & Portugal": {"countries": ["Spain", "Portugal"], "flags": ["ES", "PT"], "presented": "02 June 2026",
   "headline": "52 critical regulatory gaps in full non-compliance and 59 in partial compliance; contractor coordination (CAE) severely deficient at Valencia and Sevilla and not yet embedded at the CavyCar locations.",
   "scope": "8 sites visited (1 factory, 5 warehouses, 1 in-house warehouse, 2 offices) plus 1 remote assessment"},
 "Mexico & Colombia": {"countries": ["Mexico", "Colombia"], "flags": ["MX", "CO"], "presented": "June 2026",
   "headline": "Offices and the owned warehouse are largely compliant; EPC and in-house services carry most of the critical gaps (contractor management, lifting, LOTO, risk-assessment documentation).",
   "scope": "Owned warehouse, EPC projects, in-house services, CDMX office and Colombia home-office"},
 "France": {"countries": ["France"], "flags": ["FR"], "presented": "June 2026",
   "headline": "No requirement was evidenced as compliant: the Villeurbanne office and the EPC activity lack core documents (DUERP, prevention plan, emergency plan).",
   "scope": "Villeurbanne office and EPC activity (subcontractors and logistics provider)"},
 "Greece & Italy": {"countries": ["Greece", "Italy"], "flags": ["GR", "IT"], "presented": "June 2026",
   "headline": "Offices largely compliant; high-criticality gaps limited to Greece's risk assessment, training/drill records and Safety Technician assignment, and Italy's preposto training and earthing inspection.",
   "scope": "Athens office and Buccinasco (Milan) HQ office"},
}

json.dump({"site_figures": site_figures, "group_figures": group_figures, "cluster_figures": cluster_figures,
           "global_high": global_high, "site_gaps": site_gaps, "cluster_gaps": cluster_gaps,
           "global_gaps": global_gaps, "exec_summary": exec_summary, "cluster_meta": cluster_meta},
          open("/home/claude/amara_compliance_app/data/deck_results.json", "w"), ensure_ascii=False, indent=1)

# sanity checks against deck totals
hi = [sum(r["values"][i] for r in global_high) for i in range(3)]
print("global high C/P/NC", hi)  # deck: 184 compliant, 72 partial, 89 non-compliant

# ── v0.3: all deck TEXT is taken verbatim from deck_text_verbatim.json (extracted from the PDFs with bullet
#    structure, ✗/~ marks and sub-bullets; QA-checked twice). It replaces the hand-written text above so the
#    dashboard never shows paraphrased wording.
from pathlib import Path as _P
_vt = json.load(open(_P(__file__).with_name("deck_text_verbatim.json"), encoding="utf-8"))
_out = json.load(open("/home/claude/amara_compliance_app/data/deck_results.json", encoding="utf-8"))


def _norm_groups(groups):
    out = []
    for g in groups:
        g = dict(g)
        g["bullets"] = [b if isinstance(b, dict) else {"text": b, "mark": ""} for b in g.get("bullets", [])]
        for b in g["bullets"]:
            b.setdefault("mark", ""); b.setdefault("sub", [])
        out.append(g)
    return out


_deckname = {"Spain_Portugal": "Spain & Portugal", "Mexico_Colombia": "Mexico & Colombia", "France": "France",
             "Greece_Italy": "Greece & Italy"}
_sg = {}
for sid, panel in _vt["site_gaps"].items():
    src = f"{_deckname[panel['deck']]} cluster presentation, slide {panel['page']}"
    entry = {"panel_title": panel.get("panel_title", "Key Compliance Gaps"), "groups": _norm_groups(panel["groups"]),
             "source": src}
    if panel.get("footnote"):
        entry["footnote"] = panel["footnote"]
    if sid == "MX-SERVICES":
        for g in entry["groups"]:
            key = {"IBERDROLA": "MX-IBE", "SCHNEIDER": "MX-SCH", "BRASKEM": "MX-BRA"}[g["heading"].split()[0].upper()]
            _sg[key] = {**entry, "groups": [g]}
    _sg[sid] = entry
_out["site_gaps"] = _sg
_out["cluster_gaps"] = {cl: {"pages": v.get("pages"), "groups": _norm_groups(v["groups"])} for cl, v in _vt["cluster_gaps"].items()}
_out["global_gaps"] = {"pages": _vt["global_gaps"].get("pages"), "groups": _norm_groups(_vt["global_gaps"]["groups"])}
_out["exec_summary"] = _vt["exec_summary"]
_out["cluster_summary"] = _vt["cluster_summary"]
_out["cluster_meta"] = {cl: {"countries": m["countries"], "flags": m["flags"]} for cl, m in cluster_meta.items()}
json.dump(_out, open("/home/claude/amara_compliance_app/data/deck_results.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("verbatim deck text applied")
