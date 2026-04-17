# FoodMythBuster

> Are "healthy" food labels a lie?

Investigating whether front-of-pack health claims — *organic*, *natural*, *light*, *protein*, *zero* — are meaningful, or whether **NOVA classification** (degree of industrial processing) tells a more honest story about what we eat.

Built as a [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) capstone project.

---

## The Problem

A product can be **Nutri-Score A**, **certified organic**, and **low-fat** — and still be **NOVA Group 4** (ultra-processed). Large cohort studies link ultra-processing *itself* to cardiovascular disease, obesity and kidney issues, independent of nutrient profile ([Srour et al., BMJ 2019](https://www.bmj.com/content/365/bmj.l1451)).

In the Brazil slice of Open Food Facts, **34.3% of products carrying a front-of-pack health claim are NOVA 4** — hundreds of items marketed as "healthy" that the research says we should be eating less of.

**FoodMythBuster** is an end-to-end data pipeline that ingests Open Food Facts into a cloud data warehouse, transforms it into analytical models, and exposes the gap between health claims and ultra-processing through an interactive dashboard. It answers: *which claims, brands, categories and additives dominate the "healthy junk" segment?*

> **Scope:** this project is intentionally scoped to **Brazil-only** products from Open Food Facts. The ingestion step filters on `countries_tags = 'en:brazil'` and only keeps rows where `nova_group` is classified. Running the pipeline on a different country means swapping that filter — everything downstream (dbt models, dashboard) stays the same.

*NOVA classification: Prof. Carlos Monteiro, University of São Paulo.*

---

## Architecture

```
Open Food Facts (HuggingFace Parquet export)
            │
            ▼  dlt — extraction + schema inference
     ┌──────────────┐
     │     GCS      │  raw Parquet data lake
     └──────┬───────┘
            ▼
     ┌──────────────┐
     │   BigQuery   │  raw → staging (dbt)
     └──────┬───────┘
            ▼
     ┌──────────────┐
     │  Streamlit   │  Plotly dashboard
     └──────────────┘

  Orchestrated by Bruin · Infrastructure provisioned via Terraform
```

---

## Stack

| Layer | Tool |
|---|---|
| Data source | [Open Food Facts](https://world.openfoodfacts.org) (CC BY-SA) |
| Ingestion | [dlt](https://dlthub.com) |
| Data lake | Google Cloud Storage |
| Warehouse | BigQuery |
| Transformations | [dbt](https://www.getdbt.com) (BigQuery) · Bruin SQL (DuckDB dev) |
| Orchestration | [Bruin](https://getbruin.com) |
| Infrastructure | Terraform |
| Dashboard | Streamlit + Plotly |

---

## Key Questions

| # | Question |
|---|---|
| 1 | What share of products with a front-of-pack health claim are NOVA 4? |
| 2 | Which claims (*organic*, *light*, *protein*, *zero-sugar*, …) most often appear on ultra-processed products? |
| 3 | Which product categories are the worst offenders of "healthy junk"? |
| 4 | Which brands sell the most NOVA 4 products under health labels? |
| 5 | Which additive families dominate these deceptive products — and what does the research say about them? |
| 6 | Over time, do deceptive NOVA 4 products use *more* additives than non-deceptive ones — and is the gap widening? |

Each question maps directly to a tile in the dashboard.

---

## Dataset

**[Open Food Facts](https://world.openfoodfacts.org)** — crowdsourced, 3 M+ products globally, updated daily. Ingested via the **Parquet export** hosted on [HuggingFace](https://huggingface.co/datasets/openfoodfacts/product-database), filtered to **Brazil** products with `nova_group` classified.

Key fields: `code`, `product_name`, `nova_group` (1–4), `nutriscore_grade` (A–E), `labels_tags`, `brands`, `categories_tags`, `additives_tags`.

---

## Repo Structure

```
.
├── infra/                              # Terraform: GCS bucket + BigQuery + IAM
├── pipelines/foodmythbuster/           # Bruin orchestration
│   ├── pipeline.yml
│   └── assets/
│       ├── off_brazil_products.py      # dlt ingest · DuckDB or BigQuery
│       └── stg_products_duckdb.sql     # staging · DuckDB (dev fallback)
├── dbt/foodmythbuster/                 # dbt project · BigQuery (definitive)
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/staging/
│       ├── stg_products.sql            # partitioned + clustered staging
│       ├── sources.yml                 # declares raw.off_brazil_products
│       └── schema.yml                  # 9 schema tests
├── dashboard/
│   └── app.py                          # Streamlit + Plotly (dual backend)
├── queries/explore.sql                 # ad-hoc exploration
└── .bruin.yml.example                  # connection template
```

---

## Reproducibility

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | https://www.python.org/downloads/ |
| [Bruin CLI](https://getbruin.com) | latest | `curl -LsSf https://raw.githubusercontent.com/bruin-data/bruin/refs/heads/main/install.sh \| sh` |
| [dbt](https://www.getdbt.com) + dbt-bigquery | ≥ 1.7 | `pip install dbt-bigquery` (included in `requirements.txt`) |
| [Terraform](https://developer.hashicorp.com/terraform) | ≥ 1.5 | https://developer.hashicorp.com/terraform/install |
| `gcloud` CLI | latest | https://cloud.google.com/sdk/docs/install |

A **GCP project** with billing enabled is required for Phase 1 (cloud infra). For local-only exploration, you can skip straight to Phase 3 and run the pipeline against DuckDB.

---

### Phase 0 — Clone and install Python deps

```bash
git clone https://github.com/<your-fork>/LabelLie.git
cd LabelLie

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

### Phase 1 — Provision GCP infrastructure (Terraform)

Everything under `infra/` provisions the GCS data lake, BigQuery dataset, and pipeline service account with the correct IAM bindings. No service-account keys are created — local dev uses your own user credentials via [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials).

```bash
# 1. Authenticate to GCP (one-time per machine)
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# 2. Copy the example tfvars and fill in your values
cp infra/terraform.tfvars.example infra/terraform.tfvars
# Edit infra/terraform.tfvars:
#   project_id          = your GCP project ID
#   bucket_name_suffix  = a globally-unique suffix (e.g. your initials + year)
#   user_email          = your gcloud account email (for SA impersonation grant)

# 3. Apply
cd infra
terraform init
terraform plan -out=tfplan
terraform apply tfplan
cd ..
```

This creates roughly 11 resources: 4 API enablements, a GCS bucket (`foodmythbuster-raw-<suffix>`), a BigQuery dataset (`foodmythbuster`), a pipeline service account, and its IAM bindings (storage.objectAdmin on the bucket, bigquery.dataEditor on the dataset, bigquery.jobUser at project level).

**Verify:**

```bash
gcloud storage ls gs://foodmythbuster-raw-<suffix>
bq ls --location=southamerica-east1 YOUR_PROJECT_ID:foodmythbuster
```

Both commands should return without errors.

**Teardown** when you're done with the project:

```bash
cd infra && terraform destroy && cd ..
```

---

### Phase 2 — Configure Bruin

```bash
cp .bruin.yml.example .bruin.yml
# Edit .bruin.yml with your DuckDB path (local) or BigQuery project ID (cloud).
```

`.bruin.yml` is gitignored by design — it holds connection configs.

---

### Phase 3 — Run the pipeline

The ingestion asset picks its destination from `FOODMYTHBUSTER_TARGET` (default `duckdb`). Both paths use the **same Python asset** — only the destination differs.

**Local development (DuckDB)** — no cloud needed:

```bash
bruin run pipelines/foodmythbuster/assets/off_brazil_products.py
bruin run pipelines/foodmythbuster/assets/stg_products_duckdb.sql
```

Data lands in `data/foodmythbuster.duckdb` (schemas `raw` and `staging`).

**Cloud (BigQuery)** — definitive path:

```bash
export FOODMYTHBUSTER_TARGET=bigquery
export GCP_PROJECT_ID=your-gcp-project-id
export GCS_BUCKET=foodmythbuster-raw-<suffix>
export BQ_DATASET=foodmythbuster
export GCP_REGION=southamerica-east1

# 1. Ingest raw (dlt → GCS → BigQuery)
bruin run pipelines/foodmythbuster/assets/off_brazil_products.py

# 2. Refresh ADC token (dbt needs a fresh token for BigQuery Storage API)
gcloud auth application-default login

# 3. Transform with dbt (build + test stg_products)
cd dbt/foodmythbuster
DBT_PROFILES_DIR=. dbt run
DBT_PROFILES_DIR=. dbt test
cd ../..
```

Under the hood, dlt stages the raw Parquet into `gs://$GCS_BUCKET/` and loads it from GCS → BigQuery (`foodmythbuster.off_brazil_products`). **dbt** then materialises `foodmythbuster.stg_products`, partitioned on `created_date` and clustered on `(is_deceptive, nutriscore_grade, is_ultra_processed)` — see *Data Modeling* below — and runs 9 schema tests (`not_null`, `unique`, `accepted_values`) that enforce the pipeline's invariants as explicit contracts.

> **What you'll see in BigQuery after a cloud run:**
> - `foodmythbuster.off_brazil_products` — the authoritative raw table
> - `foodmythbuster.stg_products` — the partitioned + clustered staging model
> - `foodmythbuster._dlt_loads`, `_dlt_pipeline_state`, `_dlt_version` — dlt's internal load history and incremental cursor
> - `foodmythbuster_staging.*` — a sibling dataset dlt creates to hold the temporary merge-staging table during `write_disposition="merge"` loads. Not a transformation layer; ignore it from analytics queries.
>
> The ingestion uses backend-specific pipeline names (`foodmythbuster_duckdb` / `foodmythbuster_bq`) so incremental cursors are kept isolated — switching `FOODMYTHBUSTER_TARGET` never leaks state from one destination to the other.

> Run assets individually (not `bruin run pipelines/foodmythbuster`) when only one backend's connection is configured — the other backend's staging asset will error out otherwise.

---

### Phase 4 — Launch the dashboard

The dashboard uses `FOODMYTHBUSTER_BACKEND` to select the data source (separate from the pipeline's `FOODMYTHBUSTER_TARGET`).

**DuckDB** (default):

```bash
streamlit run dashboard/app.py
```

**BigQuery**:

```bash
export FOODMYTHBUSTER_BACKEND=bigquery
export GCP_PROJECT_ID=your-gcp-project-id
export BQ_DATASET=foodmythbuster

streamlit run dashboard/app.py
```

Streamlit opens at http://localhost:8501 with six tiles: the Nutri-Score paradox, "green label" lies, healthy-junk by category, top deceptive brands, top additive families (with linked health-concern research), and a temporal trend chart showing the widening additive gap between deceptive and non-deceptive NOVA 4 products.

Every BigQuery query is capped at **1 GB scanned** (`maximum_bytes_billed`) and cached in-process for 10 minutes (`@st.cache_data(ttl=600)`) — both safety nets against runaway costs on shared deployments.

---

## Data Modeling

The BigQuery staging table `foodmythbuster.stg_products` is physically laid out to match the dashboard's access pattern — pruning both rows and bytes-scanned at every tile.

**Partitioning** — `PARTITION BY created_date` (date the product was added to Open Food Facts).
The temporal chart (Tile 6) filters `created_date BETWEEN '2020-01-01' AND '2024-12-31'`, so BigQuery prunes all partitions outside that window before any scan. Partitioning on `created_date` also enables partition-level retention policies and cheap incremental dbt rebuilds.

**Clustering** — `CLUSTER BY is_deceptive, nutriscore_grade, is_ultra_processed`.
Five of the six tiles filter or group by one or more of these fields:

| Tile | Filter / Group | Cluster benefit |
|---|---|---|
| 1 · Nutri-Score paradox | `GROUP BY nutriscore_grade`, `is_ultra_processed` | ✓ both |
| 2 · Green label | `WHERE has_health_claim` + `is_ultra_processed` | ✓ |
| 3 · Healthy junk by category | `WHERE is_deceptive` | ✓ leading cluster key |
| 4 · Top brands | `WHERE is_deceptive` | ✓ leading cluster key |
| 5 · Top additive families | `WHERE is_deceptive` | ✓ leading cluster key |
| 6 · Temporal gap | `WHERE is_ultra_processed` + partition prune | ✓ + partition |

The Brazil slice is tiny (~5 MB), so today's savings are symbolic — the layout is chosen because it is the *correct* layout for the query pattern at any scale. When the pipeline is later re-pointed at the global OFF dataset (~3 M products, ~2 GB), the dashboard continues to read only a few MB per tile.

---

## Project Status

- [x] **Terraform:** GCS bucket, BigQuery dataset, pipeline SA, IAM (Phase 1 ✔)
- [x] Raw ingestion: Open Food Facts → DuckDB (local dev)
- [x] Staging model: cleaned, health-claim and NOVA flags derived
- [x] Streamlit + Plotly dashboard — 6 tiles + health references
- [x] Migrate ingestion target from DuckDB to GCS / BigQuery (env-var switch)
- [x] Temporal trend tile on the dashboard (deceptive vs non-deceptive additive gap)
- [x] dbt models on BigQuery (staging + 9 schema tests)
- [ ] Deploy dashboard (Streamlit Community Cloud or GCP Cloud Run)
