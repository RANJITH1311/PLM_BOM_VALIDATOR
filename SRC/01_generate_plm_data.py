import os
import pandas as pd

os.makedirs("data/raw", exist_ok=True)

# Multi-level Engineering BOM for a 1MW PEM Electrolyzer Stack
bom_data = [
    # Level 0: Top Assembly
    {"parent_id": "ROOT", "part_number": "ASM-1000", "rev": "B", "description": "PEM Electrolyzer Stack 1MW", "lifecycle_state": "Released", "material": "Assembly", "weight_kg": 0.0, "unit_cost_eur": 0.0, "qty": 1, "cad_file_linked": True, "supplier_code": "INTERNAL"},
    
    # Level 1: Sub-assemblies
    {"parent_id": "ASM-1000", "part_number": "SUB-2100", "rev": "C", "description": "Cell Stack Core Module", "lifecycle_state": "Released", "material": "Assembly", "weight_kg": 0.0, "unit_cost_eur": 0.0, "qty": 1, "cad_file_linked": True, "supplier_code": "INTERNAL"},
    {"parent_id": "ASM-1000", "part_number": "SUB-2200", "rev": "A", "description": "End Plate & Compression Frame", "lifecycle_state": "Released", "material": "Assembly", "weight_kg": 0.0, "unit_cost_eur": 0.0, "qty": 2, "cad_file_linked": True, "supplier_code": "INTERNAL"},
    {"parent_id": "ASM-1000", "part_number": "SUB-2300", "rev": "B", "description": "Coolant Manifold Assembly", "lifecycle_state": "In Work", "material": "Assembly", "weight_kg": 0.0, "unit_cost_eur": 0.0, "qty": 1, "cad_file_linked": False, "supplier_code": "INTERNAL"}, # DEFECT 1: Released parent has 'In Work' child

    # Level 2: Components under SUB-2100
    {"parent_id": "SUB-2100", "part_number": "PRT-3001", "rev": "B", "description": "Bipolar Plate Titanium", "lifecycle_state": "Released", "material": "Ti-6Al-4V", "weight_kg": 1.45, "unit_cost_eur": 85.00, "qty": 120, "cad_file_linked": True, "supplier_code": "SUP-881"},
    {"parent_id": "SUB-2100", "part_number": "PRT-3002", "rev": "A", "description": "Membrane Electrode Assembly (MEA)", "lifecycle_state": "Released", "material": "PFSA-Pt/Ir", "weight_kg": 0.12, "unit_cost_eur": 210.00, "qty": 120, "cad_file_linked": True, "supplier_code": "SUP-904"},
    {"parent_id": "SUB-2100", "part_number": "PRT-3003", "rev": "A", "description": "EPDM Perimeter Gasket", "lifecycle_state": "Released", "material": "", "weight_kg": 0.04, "unit_cost_eur": 3.50, "qty": 240, "cad_file_linked": False, "supplier_code": "SUP-412"}, # DEFECT 2 & 3: Missing material & missing CAD link

    # Level 2: Components under SUB-2200
    {"parent_id": "SUB-2200", "part_number": "PRT-3010", "rev": "A", "description": "Structural Compression Plate", "lifecycle_state": "Released", "material": "EN 1.4404 (316L)", "weight_kg": 48.50, "unit_cost_eur": 420.00, "qty": 1, "cad_file_linked": True, "supplier_code": "SUP-119"},
    {"parent_id": "SUB-2200", "part_number": "PRT-3011", "rev": "D", "description": "M16 Tie Rod Bolt", "lifecycle_state": "Obsolete", "material": "A4-80 Stainless", "weight_kg": 0.85, "unit_cost_eur": 12.00, "qty": 16, "cad_file_linked": True, "supplier_code": "SUP-205"}, # DEFECT 4: Obsolete part used in active BOM
    {"parent_id": "SUB-2200", "part_number": "PRT-3011", "rev": "D", "description": "M16 Tie Rod Bolt", "lifecycle_state": "Obsolete", "material": "A4-80 Stainless", "weight_kg": 0.85, "unit_cost_eur": 12.00, "qty": 16, "cad_file_linked": True, "supplier_code": "SUP-205"}, # DEFECT 5: Duplicate BOM line item

    # Level 2: Components under SUB-2300
    {"parent_id": "SUB-2300", "part_number": "PRT-3020", "rev": "B", "description": "Deionized Water Inlet Valve", "lifecycle_state": "Released", "material": "PTFE / 316L", "weight_kg": 2.10, "unit_cost_eur": 145.00, "qty": 2, "cad_file_linked": True, "supplier_code": ""}, # DEFECT 6: Missing supplier code on purchased part
    {"parent_id": "SUB-2300", "part_number": "PRT-3021", "rev": "A", "description": "Temperature Sensor PT100", "lifecycle_state": "Released", "material": "316L", "weight_kg": 0.0, "unit_cost_eur": 38.00, "qty": 4, "cad_file_linked": True, "supplier_code": "SUP-330"}, # DEFECT 7: Zero weight on physical leaf part

    # Orphan component (not linked to any valid parent)
    {"parent_id": "SUB-9999", "part_number": "PRT-3099", "rev": "A", "description": "Unassigned Lifting Bracket", "lifecycle_state": "Released", "material": "S235JR", "weight_kg": 3.20, "unit_cost_eur": 25.00, "qty": 2, "cad_file_linked": True, "supplier_code": "SUP-119"} # DEFECT 8: Orphaned parent reference
]

df_bom = pd.DataFrame(bom_data)
df_bom.to_csv("data/raw/engineering_bom_v1.csv", index=False)
print("SUCCESS: Created data/raw/engineering_bom_v1.csv with 13 rows.")