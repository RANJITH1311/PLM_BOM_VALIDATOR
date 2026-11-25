# Automated PLM BOM Data Quality & Change-Control Validator

An automated **Python, SQLite, and Power BI** data governance engine that audits multi-level engineering Bills of Materials (BOMs) for lifecycle maturity mismatches, missing 3D CAD/material metadata, orphaned parts, and circular references prior to manufacturing release.

## Dashboard Preview
![PLM Data Quality Dashboard](POWER%20BI/dashboard_overview.png?v=2)

---

## Business Problem & Engineering Context
In enterprise Product Lifecycle Management (PLM) environments (such as Siemens Teamcenter or Dassault 3DEXPERIENCE), engineering assemblies fail downstream ERP/SAP handover when components contain incomplete metadata, obsolete revisions, or unapproved child parts. 

Using a **1 MW PEM Electrolyzer Stack (`ASM-1000`)** as a reference assembly, this tool automates release-gate quality assurance, performs recursive bottom-up mass/cost roll-ups, and quantifies the impact of Engineering Change Orders (ECOs).

---

## Automated PLM Release-Gate Rules (`02_bom_validator.py`)

| Rule ID | Check Category | Severity | Engineering Governance Logic |
| :--- | :--- | :--- | :--- |
| **PLM-001** | Duplicate Entry | Critical | Flags identical `(parent_id, part_number, rev)` rows to prevent double-ordering. |
| **PLM-002** | Orphaned Part | Critical | Verifies every `parent_id` resolves to an existing parent assembly in the BOM tree. |
| **PLM-003** | Lifecycle Mismatch | Critical | Blocks `Released` assemblies from containing `In Work` or unapproved child items. |
| **PLM-004** | Obsolete Part | Critical | Prevents `Obsolete` components from being referenced in active production BOMs. |
| **PLM-005** | Missing Material | Major | Requires valid material grade specifications on all physical leaf components. |
| **PLM-006** | Zero Weight | Minor | Flags physical components with `0.0 kg` mass so 3D CAD mass properties are updated. |
| **PLM-007** | Missing Supplier | Major | Ensures all non-internal purchased parts carry an approved vendor code. |
| **PLM-008** | Missing CAD Link | Major | Verifies every active item has a linked 3D CAD model (`.prt` / `.step`) in the PLM vault. |

---

## Key Technical Results

* **Audit & Data Health:** Detected **12 total governance violations** across 8 defective line items (including lifecycle maturity mismatches, duplicate tie-rod bolts, and missing NX/STEP links) and exported structured reports to Excel (`bom_validation_report.xlsx`) and SQLite (`plm_governance.db`).
* **Graph-Based Mass & Cost Roll-Up (`NetworkX`):** Modeled the multi-level BOM as a Directed Acyclic Graph (DAG) to verify zero circular references (`nx.simple_cycles`) and calculate bottom-up assembly totals (**€37,396.00** top-level stack cost).
* **ECO Impact Simulation (`03_eco_impact_analyzer.py`):** Simulated `ECO-2026-04` (substituting 316L stainless compression plates with AlMg4.5Mn alloy), automatically calculating a **-53.0 kg** assembly weight reduction and **-€120.00** unit cost savings.

### Core Roll-Up Logic (`SRC/02_bom_validator.py`)
```python
def compute_rollup(part_num):
    children = list(G.successors(part_num))
    if not children:
        return part_meta[part_num]["weight_kg"], part_meta[part_num]["unit_cost_eur"]
    total_w, total_c = 0.0, 0.0
    for child in children:
        qty = G[part_num][child]["qty"]
        w, c = compute_rollup(child)
        total_w += w * qty
        total_c += c * qty
    return total_w, total_c