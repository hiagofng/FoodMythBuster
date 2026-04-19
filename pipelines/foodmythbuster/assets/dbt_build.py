"""@bruin
name: foodmythbuster.dbt_build
type: python
depends:
  - raw.off_brazil_products
@bruin"""

import logging
import os
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

TARGET = os.getenv("FOODMYTHBUSTER_TARGET", "duckdb").lower()

PROJECT_DIR = Path(__file__).resolve().parents[3] / "dbt" / "foodmythbuster"

env = {**os.environ, "DBT_PROFILES_DIR": str(PROJECT_DIR)}
target_flag = [] if TARGET == "bigquery" else ["--target", "duckdb"]

log.info("Running dbt build in %s (FOODMYTHBUSTER_TARGET=%s)", PROJECT_DIR, TARGET)
subprocess.run(
    ["dbt", "build", "--project-dir", str(PROJECT_DIR), *target_flag],
    check=True,
    env=env,
)
