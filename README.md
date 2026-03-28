# FoodMythBuster

> Are "healthy" food labels a lie?

Investigating whether front-of-pack health claims — *organic*, *natural*, *light*, *protein*, *zero* — are meaningful, or whether **NOVA classification** (degree of industrial processing) tells a more honest story about what we eat.

Built as a [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) capstone project.

---

## The Problem

A product can be **Nutri-Score A**, **certified organic**, and **low-fat** — and still be **NOVA Group 4** (ultra-processed). Large epidemiological cohort studies consistently link ultra-processing to obesity, cardiovascular disease, and depression — independent of nutrient profile.

*NOVA classification: Prof. Carlos Monteiro, University of São Paulo.*

---

## Architecture

```
Open Food Facts API (REST v2)
          │
          ▼
  ┌───────────────┐
  │  Bruin        │  pipeline orchestration
  └───────┬───────┘
          │
   ┌──────┴──────┐
   │   raw.*     │  DuckDB (local dev)
   └──────┬──────┘      ↳ planned: GCS data lake → BigQuery
          │
   ┌──────┴──────┐
   │ staging.*   │  Bruin SQL assets
   └──────┬──────┘
          │
   ┌──────┴──────┐
   │  Streamlit  │  Plotly dashboards  (planned)
   └─────────────┘
```

---

## Stack

| Layer | Tool | Notes |
|---|---|---|
| Orchestration | [Bruin](https://getbruin.com) | pipeline + SQL asset management |
| Warehouse — local | DuckDB | |
| Warehouse — cloud | BigQuery | *planned* |
| Infrastructure | Terraform | *planned* |
| Dashboard | Streamlit + Plotly | *planned* |
| Data source | Open Food Facts API v2 | CC BY-SA licence |

---

## Key Questions

| # | Question |
|---|---|
| 1 | What % of products with health claims are NOVA 4 (ultra-processed)? |
| 2 | Which brands carry the most NOVA 4 products despite health claims? |
| 3 | Nutri-Score A products that are still NOVA 4 — the paradox |
| 4 | Brazil vs USA vs France — who is most deceived? |
| 5 | Which categories deceive most? (cereals, protein bars, plant-based) |

---

## Dataset

**[Open Food Facts](https://world.openfoodfacts.org)** — crowdsourced, 3 M+ products globally, updated daily, free REST API.
Initial scope: **Brazil**, products where `nova_group` is already classified.

Key fields: `code`, `product_name`, `nova_group` (1–4), `nutriscore_grade` (A–E), `labels_tags`, `brands`, `categories_tags`, `additives_tags`.

---

## Repo Structure

```
.
├── .bruin.yml                      # Bruin connections config
├── pipelines/foodmythbuster/
│   └── pipeline.yml                # schedule + pipeline metadata
├── assets/
│   ├── raw/
│   │   └── off_brazil_products.py  # ingest: API → DuckDB raw layer
│   └── staging/
│       └── stg_products.sql        # transform: clean + derive flags
├── queries/
│   └── explore.sql                 # ad-hoc exploration queries
└── data/                           # gitignored — holds .duckdb file
```

---

## Setup

**Prerequisites:** Python 3.11+, [Bruin CLI](https://getbruin.com/docs/getting-started/), DuckDB CLI (optional).

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Ingest raw data (Brazil — expect 10–30 min, API-dependent)
bruin run assets/raw/off_brazil_products.py

# 3. Build staging model
bruin run assets/staging/stg_products.sql

# 4. Explore
duckdb data/foodmythbuster.duckdb < queries/explore.sql
```

Or run the full pipeline end-to-end:

```bash
bruin run pipelines/foodmythbuster/pipeline.yml
```

---

## Project Status

- [x] Scaffold + pipeline config
- [x] Raw ingestion: Open Food Facts API → DuckDB
- [x] Staging model: cleaned + health claim + NOVA flags
- [ ] Cloud layer: GCS data lake + BigQuery warehouse
- [ ] Terraform for infra provisioning
- [ ] dbt transformations on BigQuery
- [ ] Streamlit + Plotly dashboard (5 charts)
