# Automated PLM BOM Data Quality & Change-Control Validator

An automated Python, SQLite, and Power BI data governance tool that audits multi-level engineering Bills of Materials (BOMs) for lifecycle maturity mismatches, missing CAD/material metadata, orphaned parts, and circular references prior to manufacturing release.

## Dashboard Preview
![PLM Data Quality Dashboard](POWER%20BI/dashboard_overview.png)

## Key Features
* **Automated Rule Engine (`02_bom_validator.py`):** Validates 8 core PLM release-gate rules across multi-level assemblies.
* **Graph-Based Mass & Cost Roll-Up (`NetworkX`):** Models parent-child hierarchies as a Directed Acyclic Graph (DAG) to detect circular references and calculate bottom-up assembly weight and cost.
* **ECO Impact Simulator (`03_eco_impact_analyzer.py`):** Quantifies weight (`-53.0 kg`) and cost (`-€120.00`) deltas when substituting materials under an Engineering Change Order.
* **Technical Documentation (`docs/PLM_Data_Standard_SOP.md`):** Standard Operating Procedure defining part-numbering schemas and release-gate governance rules.

## How to Run
```bash
pip install pandas networkx openpyxl
python src/01_generate_plm_data.py
python src/02_bom_validator.py
python src/03_eco_impact_analyzer.py
