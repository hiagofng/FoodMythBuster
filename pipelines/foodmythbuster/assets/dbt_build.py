"""@bruin
name: foodmythbuster.dbt_build
type: python
depends:
  - raw.off_brazil_products
@bruin"""

import logging
import os
import subprocess
import sys
from pathlib import Path

log = logging.getLogger(__name__)

TARGET = os.getenv("FOODMYTHBUSTER_TARGET", "duckdb").lower()

# The DuckDB backend has its own transformation asset (stg_products_duckdb.sql).
# This asset only runs when the pipeline is pointed at BigQuery so the two
# backends keep a clean two-node DAG each.
if TARGET != "bigquery":
    log.info("dbt_build skipped (FOODMYTHBUSTER_TARGET=%s, not bigquery)", TARGET)
    sys.exit(0)

PROJECT_DIR = Path(__file__).resolve().parents[3] / "dbt" / "foodmythbuster"

env = {**os.environ, "DBT_PROFILES_DIR": str(PROJECT_DIR)}

log.info("Running dbt build in %s", PROJECT_DIR)
subprocess.run(
    ["dbt", "build", "--project-dir", str(PROJECT_DIR)],
    check=True,
    env=env,
)
