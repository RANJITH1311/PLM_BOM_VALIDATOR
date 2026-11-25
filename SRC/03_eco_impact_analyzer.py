import pandas as pd

df_v1 = pd.read_excel("data/output/bom_validation_report.xlsx", sheet_name="Assembly_Rollups")

# Simulate Revision B -> C Engineering Change Order (ECO-2026-04):
# Replacing heavy 316L Compression Plate (48.5 kg, €420) with lighter AlMg4.5Mn plate (22.0 kg, €360)
df_v2 = pd.read_csv("data/raw/engineering_bom_v1.csv").drop_duplicates(subset=["parent_id", "part_number", "rev"]).copy()
df_v2.loc[df_v2["part_number"] == "PRT-3010", ["weight_kg", "unit_cost_eur", "rev"]] = [22.0, 360.0, "B"]

old_weight = df_v1.loc[df_v1["part_number"] == "ASM-1000", "rolled_up_weight_kg"].values[0]
old_cost = df_v1.loc[df_v1["part_number"] == "ASM-1000", "rolled_up_cost_eur"].values[0]

weight_delta = (22.0 - 48.5) * 2
cost_delta = (360.0 - 420.0) * 2

eco_summary = pd.DataFrame([{
    "eco_id": "ECO-2026-04",
    "affected_part": "PRT-3010 (Compression Plate)",
    "top_assembly": "ASM-1000",
    "old_total_weight_kg": old_weight,
    "new_total_weight_kg": round(old_weight + weight_delta, 2),
    "weight_change_kg": round(weight_delta, 2),
    "old_total_cost_eur": old_cost,
    "new_total_cost_eur": round(old_cost + cost_delta, 2),
    "cost_change_eur": round(cost_delta, 2)
}])

eco_summary.to_csv("data/output/eco_impact_summary.csv", index=False)
print("ECO Impact Analysis Complete:")
print(eco_summary.to_string(index=False))