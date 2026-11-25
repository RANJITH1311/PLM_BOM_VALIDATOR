import os
import sqlite3
import pandas as pd
import networkx as nx

os.makedirs("data/output", exist_ok=True)
df = pd.read_csv("data/raw/engineering_bom_v1.csv")

issues = []

def log_issue(row, rule_id, category, severity, message):
    issues.append({
        "rule_id": rule_id,
        "category": category,
        "severity": severity,
        "parent_id": row["parent_id"],
        "part_number": row["part_number"],
        "rev": row["rev"],
        "description": row["description"],
        "issue_details": message
    })

# Rule 1: Duplicate BOM Line Check
duplicates = df[df.duplicated(subset=["parent_id", "part_number", "rev"], keep=False)]
for _, row in duplicates.drop_duplicates(subset=["parent_id", "part_number"]).iterrows():
    log_issue(row, "PLM-001", "Duplicate Entry", "Critical", "Duplicate parent-child BOM entry detected; consolidate quantities.")

# Rule 2-8: Hierarchy, Lifecycle & Attribute Checks
valid_parts = set(df["part_number"]).union({"ROOT"})
state_lookup = df.set_index("part_number")["lifecycle_state"].to_dict()

for _, row in df.iterrows():
    if row["parent_id"] not in valid_parts:
        log_issue(row, "PLM-002", "Orphaned Part", "Critical", f"Parent '{row['parent_id']}' does not exist in BOM.")
    
    if row["parent_id"] in state_lookup:
        if state_lookup[row["parent_id"]] == "Released" and row["lifecycle_state"] != "Released":
            log_issue(row, "PLM-003", "Lifecycle Mismatch", "Critical", f"Released parent contains '{row['lifecycle_state']}' child.")

    if row["lifecycle_state"] == "Obsolete":
        log_issue(row, "PLM-004", "Obsolete Part", "Critical", "Obsolete component referenced in active assembly.")

    is_leaf = row["material"] != "Assembly"
    if is_leaf:
        if pd.isna(row["material"]) or str(row["material"]).strip() == "":
            log_issue(row, "PLM-005", "Missing Material", "Major", "Missing material specification on component.")
        if row["weight_kg"] <= 0:
            log_issue(row, "PLM-006", "Zero Weight", "Minor", "Physical component has 0.0 kg mass; update CAD properties.")
        if row["supplier_code"] != "INTERNAL" and (pd.isna(row["supplier_code"]) or str(row["supplier_code"]).strip() == ""):
            log_issue(row, "PLM-007", "Missing Supplier", "Major", "Purchased part missing approved vendor code.")
    
    if not row["cad_file_linked"]:
        log_issue(row, "PLM-008", "Missing CAD Link", "Major", "Missing 3D CAD geometry link (NX/STEP) in PLM vault.")

df_issues = pd.DataFrame(issues)

# Build Graph & Calculate Bottom-Up Mass & Cost Roll-Up
df_clean = df.drop_duplicates(subset=["parent_id", "part_number", "rev"]).copy()
G = nx.DiGraph()

# Add every part as a node first (so even orphaned parts exist in the graph)
for _, r in df_clean.iterrows():
    G.add_node(r["part_number"])
    if r["parent_id"] in valid_parts and r["parent_id"] != "ROOT":
        G.add_edge(r["parent_id"], r["part_number"], qty=r["qty"])

assert len(list(nx.simple_cycles(G))) == 0, "Circular BOM reference detected!"

part_meta = df_clean.set_index("part_number").to_dict("index")

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

rollups = []
for p in part_meta:
    w, c = compute_rollup(p)
    rollups.append({
        "part_number": p,
        "parent_id": part_meta[p]["parent_id"],
        "description": part_meta[p]["description"],
        "lifecycle_state": part_meta[p]["lifecycle_state"],
        "qty": part_meta[p]["qty"],
        "rolled_up_weight_kg": round(w, 2),
        "rolled_up_cost_eur": round(c, 2)
    })

df_rollups = pd.DataFrame(rollups)

# Export to Excel & SQLite
with pd.ExcelWriter("data/output/bom_validation_report.xlsx", engine="openpyxl") as writer:
    df_issues.to_excel(writer, sheet_name="Validation_Errors", index=False)
    df_rollups.to_excel(writer, sheet_name="Assembly_Rollups", index=False)
    df_clean.to_excel(writer, sheet_name="Cleaned_BOM", index=False)

conn = sqlite3.connect("data/output/plm_governance.db")
df_issues.to_sql("bom_validation_issues", conn, if_exists="replace", index=False)
df_rollups.to_sql("assembly_rollups", conn, if_exists="replace", index=False)
df_clean.to_sql("engineering_bom", conn, if_exists="replace", index=False)
conn.close()

print(f"AUDIT COMPLETE: Found {len(df_issues)} PLM governance defects.")
print("Saved Excel report to: data/output/bom_validation_report.xlsx")
print("Saved SQLite DB to:    data/output/plm_governance.db")