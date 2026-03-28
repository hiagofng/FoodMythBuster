""" @bruin
name: raw.off_brazil_products
type: python
description: "Fetch Brazilian products from Open Food Facts API — only rows with NOVA group filled"
"""

import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

API_BASE = "https://world.openfoodfacts.org/api/v2/search"
FIELDS = (
    "code,product_name,nova_group,nutriscore_grade,"
    "labels_tags,brands,categories_tags,additives_tags,ingredients_text"
)
PAGE_SIZE = 1000
# Override via env var if needed (e.g. in CI or cloud runs)
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "data/foodmythbuster.duckdb")


def fetch_page(session: requests.Session, page: int) -> dict:
    params = {
        "countries_tags_en": "brazil",
        "fields": FIELDS,
        "page_size": PAGE_SIZE,
        "page": page,
    }
    resp = session.get(API_BASE, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def to_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    Path(DUCKDB_PATH).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(DUCKDB_PATH)

    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute("CREATE SCHEMA IF NOT EXISTS staging")  # pre-create for downstream assets
    con.execute("""
        CREATE OR REPLACE TABLE raw.off_brazil_products (
            code              VARCHAR,
            product_name      VARCHAR,
            nova_group        TINYINT,
            nutriscore_grade  VARCHAR,
            labels_tags       VARCHAR[],
            brands            VARCHAR,
            categories_tags   VARCHAR[],
            additives_tags    VARCHAR[],
            ingredients_text  VARCHAR,
            ingested_at       TIMESTAMPTZ
        )
    """)

    session = requests.Session()
    session.headers["User-Agent"] = (
        "FoodMythBuster/1.0 (data-eng-zoomcamp capstone; contact via GitHub)"
    )

    ingested_at = datetime.now(timezone.utc)
    page, total = 1, 0

    while True:
        log.info("Fetching page %d …", page)
        data = fetch_page(session, page)
        products = data.get("products", [])

        if not products:
            break

        rows = [
            (
                p.get("code"),
                p.get("product_name"),
                to_int(p.get("nova_group")),
                p.get("nutriscore_grade"),
                p.get("labels_tags") or [],
                p.get("brands"),
                p.get("categories_tags") or [],
                p.get("additives_tags") or [],
                p.get("ingredients_text"),
                ingested_at,
            )
            for p in products
            if to_int(p.get("nova_group")) is not None  # skip products without NOVA label
        ]

        if rows:
            con.executemany(
                "INSERT INTO raw.off_brazil_products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
            total += len(rows)
            log.info("  +%d rows  (running total: %d)", len(rows), total)

        page_count = data.get("page_count", 1)
        if page >= page_count:
            break

        page += 1
        time.sleep(0.5)  # be polite to the public API

    log.info("Ingestion complete — %d rows written to raw.off_brazil_products", total)
    con.close()


main()
