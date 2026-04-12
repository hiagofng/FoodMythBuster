# Incremental Loading — OFF Parquet via dlt

## How it works

1. Bruin runs the pipeline on schedule (`@daily`)
2. Python asset re-downloads the Parquet if a newer version exists (checks `Last-Modified` header)
3. dlt reads the Parquet, filters to Brazil (789/790 barcodes), and only loads rows where `last_modified_t > last_stored_value`
4. dlt tracks the high-water mark automatically between runs

---

## Step 1 — Update `off_brazil_products.py`

Replace the full file with:

```python
"""@bruin
name: raw.off_brazil_products
type: python
@bruin"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import dlt
import duckdb
import requests

log = logging.getLogger(__name__)

PARQUET_URL = (
    "https://huggingface.co/datasets/openfoodfacts/product-database"
    "/resolve/main/food.parquet"
)
PARQUET_LOCAL = os.getenv("PARQUET_LOCAL", "data/openfoodfacts.parquet")
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "data/foodmythbuster.duckdb")

COLUMNS = [
    "code", "product_name", "nova_group", "nutriscore_grade",
    "labels_tags", "brands", "categories_tags", "additives_tags",
    "ingredients_text", "last_modified_t",
]


def _download_parquet(force: bool = False):
    """Download OFF Parquet if remote is newer than local copy."""
    path = Path(PARQUET_LOCAL)
    path.parent.mkdir(parents=True, exist_ok=True)

    headers = {}
    if path.exists() and not force:
        # Only download if remote file is newer
        local_mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        headers["If-Modified-Since"] = local_mtime.strftime("%a, %d %b %Y %H:%M:%S GMT")

    log.info("Checking for updated Parquet …")
    resp = requests.get(PARQUET_URL, headers=headers, stream=True, timeout=600)

    if resp.status_code == 304:
        log.info("Parquet is up to date, skipping download")
        return

    resp.raise_for_status()
    with open(path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            f.write(chunk)
    log.info("Downloaded fresh Parquet: %.0f MB", path.stat().st_size / 1e6)


@dlt.resource(
    name="off_brazil_products",
    write_disposition="merge",
    primary_key="code",
)
def off_brazil_products(
    last_modified: dlt.sources.incremental[int] = dlt.sources.incremental(
        "last_modified_t", initial_value=0
    ),
):
    """Load Brazil products incrementally based on last_modified_t."""
    _download_parquet()

    cutoff = last_modified.last_value
    log.info("Incremental cutoff: last_modified_t > %d", cutoff)

    con = duckdb.connect()
    result = con.execute(f"""
        SELECT
            code,
            product_name[1].text            AS product_name,
            CAST(nova_group AS INTEGER)     AS nova_group,
            nutriscore_grade,
            labels_tags,
            brands,
            categories_tags,
            additives_tags,
            ingredients_text[1].text        AS ingredients_text,
            last_modified_t
        FROM read_parquet('{PARQUET_LOCAL}')
        -- GS1 prefixes 789/790 = barcodes issued in Brazil
        WHERE (code LIKE '789%' OR code LIKE '790%')
          AND nova_group IS NOT NULL
          AND len(product_name) > 0
          AND last_modified_t > {cutoff}
    """)

    array_cols = {"labels_tags", "categories_tags", "additives_tags"}
    total = 0

    while batch := result.fetchmany(1000):
        for row in batch:
            record = dict(zip(COLUMNS, row))
            for col in array_cols:
                record[col] = json.dumps(record[col] or [])
            yield record
        total += len(batch)

    con.close()
    log.info("Yielded %d new/updated products", total)


def main():
    pipeline = dlt.pipeline(
        pipeline_name="foodmythbuster",
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name="raw",
    )
    load_info = pipeline.run(off_brazil_products())
    log.info("dlt load complete: %s", load_info)


main()
```

---

## Key changes from current version

| What | Before | After |
|---|---|---|
| `write_disposition` | `replace` (full refresh) | `merge` (upsert by `code`) |
| Incremental cursor | none | `last_modified_t` — dlt tracks high-water mark |
| Parquet download | skip if file exists | check `Last-Modified` header, re-download only if newer |
| `primary_key` | none | `code` (barcode) — used for merge/upsert |

---

## Step 2 — Reset for first run

Since we're switching from `replace` to `merge`, reset the dlt pipeline state:

```bash
# Delete dlt cached state
rm -rf ~/.dlt/pipelines/foodmythbuster

# Drop existing raw table (optional — merge will create it)
python -c "
import duckdb
con = duckdb.connect('data/foodmythbuster.duckdb')
con.execute('DROP TABLE IF EXISTS raw.off_brazil_products')
con.execute('DROP TABLE IF EXISTS raw._dlt_loads')
con.execute('DROP TABLE IF EXISTS raw._dlt_pipeline_state')
con.execute('DROP TABLE IF EXISTS raw._dlt_version')
con.close()
"
```

---

## Step 3 — First run (full load)

```bash
bruin run pipelines/foodmythbuster/assets/off_brazil_products.py
bruin run pipelines/foodmythbuster/assets/stg_products.sql
```

First run loads everything since `initial_value=0` (all products ever modified).

---

## Step 4 — Subsequent runs (incremental)

Same command — dlt remembers the highest `last_modified_t` from the previous run and only loads newer rows:

```bash
bruin run pipelines/foodmythbuster/pipeline.yml
```

---

## How dlt incremental works under the hood

1. `dlt.sources.incremental("last_modified_t", initial_value=0)` — tells dlt to track this column
2. On each run, dlt reads `last_value` from `~/.dlt/pipelines/foodmythbuster/state.json`
3. Your resource filters `WHERE last_modified_t > cutoff`
4. After the run, dlt saves the new max `last_modified_t` as the next cutoff
5. `write_disposition="merge"` + `primary_key="code"` — upserts: inserts new products, updates existing ones

---

## Notes

- The Parquet on HuggingFace is regenerated **daily** — so daily schedule matches the source cadence
- `If-Modified-Since` header avoids re-downloading if the Parquet hasn't changed
- If you ever need a full refresh, delete the dlt state: `rm -rf ~/.dlt/pipelines/foodmythbuster`
