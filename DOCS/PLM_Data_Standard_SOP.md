# Standard Operating Procedure: PLM BOM Governance & Release Gate Rules

## 1. Purpose
This document defines mandatory data quality standards for engineering Bills of Materials (BOMs) prior to manufacturing release (`Released` lifecycle state) or ERP handover.

## 2. Part Numbering Schema
* **`ASM-XXXX`**: Top-level sellable product assemblies.
* **`SUB-XXXX`**: Functional sub-assemblies (e.g., Cell Stack, Cooling Loop).
* **`PRT-XXXX`**: Individual manufactured components or purchased catalog items.

## 3. Mandatory Release Gate Rules
Before transitioning any item from `In Work` to `Released`, the automated validator (`02_bom_validator.py`) must verify:
1. **No Duplicate Lines (`PLM-001`):** Identical `(parent_id, part_number, rev)` tuples must be consolidated into a single quantity line.
2. **Referential Integrity (`PLM-002`):** Every `parent_id` must resolve to an existing assembly in the BOM hierarchy (no orphaned parts).
3. **Lifecycle Maturity Alignment (`PLM-003`):** A `Released` parent assembly cannot contain `In Work` or `Obsolete` child components.
4. **Zero Obsolete Parts (`PLM-004`):** Components marked `Obsolete` must be superseded via an Engineering Change Order (ECO) before assembly release.
5. **Material & Mass Completeness (`PLM-005`, `PLM-006`):** All physical leaf parts must specify a valid material grade and non-zero mass derived from 3D CAD properties.
6. **Supplier Traceability (`PLM-007`):** Non-internal purchased parts must contain an approved vendor/supplier code.
7. **3D CAD Vault Linkage (`PLM-008`):** Every active part must have a verified link to its native CAD/STEP file.