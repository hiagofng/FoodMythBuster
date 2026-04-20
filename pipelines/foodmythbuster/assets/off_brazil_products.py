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

# duckdb (default) for local dev · bigquery for cloud
TARGET = os.getenv("FOODMYTHBUSTER_TARGET", "duckdb").lower()

# brazil (default) filters GS1 prefixes 789/790 · global loads every country
SCOPE = os.getenv("FOODMYTHBUSTER_SCOPE", "brazil").lower()

COLUMNS = [
    "code", "product_name", "nova_group", "nutriscore_grade",
    "labels_tags", "brands", "categories", "categories_tags",
    "additives_tags", "additives_n", "ingredients_text", "ingredients_n",
    "created_t", "last_modified_t",
]


def _download_parquet(force: bool = False):
    """Download OFF Parquet if remote is newer than local copy."""
    path = Path(PARQUET_LOCAL)
    path.parent.mkdir(parents=True, exist_ok=True)

    headers = {}
    if path.exists() and not force:
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
    """Load Brazil products incrementally based on last_modified_t.

    Array columns (labels_tags, categories_tags, additives_tags) are
    JSON-serialised before yielding so dlt keeps them as a single VARCHAR
    column instead of normalising them into child tables. Staging models
    parse the JSON back into native arrays.
    """
    _download_parquet()

    cutoff = last_modified.last_value
    log.info("Incremental cutoff: last_modified_t > %d", cutoff)
    log.info("Scope: %s", SCOPE)

    # GS1 prefixes 789/790 = barcodes issued in Brazil
    scope_filter = (
        "(code LIKE '789%' OR code LIKE '790%') AND"
        if SCOPE == "brazil"
        else ""
    )

    con = duckdb.connect()
    result = con.execute(f"""
        SELECT
            code,
            product_name[1].text            AS product_name,
            CAST(nova_group AS INTEGER)     AS nova_group,
            nutriscore_grade,
            labels_tags,
            brands,
            categories,
            categories_tags,
            additives_tags,
            additives_n,
            ingredients_text[1].text        AS ingredients_text,
            ingredients_n,
            created_t,
            last_modified_t
        FROM read_parquet('{PARQUET_LOCAL}')
        WHERE {scope_filter}
              nova_group IS NOT NULL
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


def _build_pipeline():
    if TARGET == "bigquery":
        os.environ["DESTINATION__BIGQUERY__CREDENTIALS__PROJECT_ID"] = os.environ["GCP_PROJECT_ID"]
        os.environ.setdefault(
            "DESTINATION__BIGQUERY__LOCATION",
            os.getenv("GCP_REGION", "southamerica-east1"),
        )
        os.environ["DESTINATION__FILESYSTEM__BUCKET_URL"] = f"gs://{os.environ['GCS_BUCKET']}"
        return dlt.pipeline(
            pipeline_name=f"foodmythbuster_bq_{SCOPE}",
            destination="bigquery",
            staging="filesystem",
            dataset_name=os.getenv("BQ_DATASET", "foodmythbuster"),
        )
    
    return dlt.pipeline(
        pipeline_name=f"foodmythbuster_duckdb_{SCOPE}",
        destination=dlt.destinations.duckdb(DUCKDB_PATH),
        dataset_name="raw",
    )


def main():
    log.info("Ingestion target: %s", TARGET)
    pipeline = _build_pipeline()
    load_info = pipeline.run(off_brazil_products(), loader_file_format="parquet")
    log.info("dlt load complete: %s", load_info)


main()
