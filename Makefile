# FoodMythBuster — one-command runners
SHELL := /bin/bash

ifneq (,$(wildcard .env))
    include .env
    export
endif

export DATA_WRITER__LOADER_FILE_FORMAT=parquet
export DUCKDB_PATH=data/foodmythbuster.duckdb

DBT_DIR := dbt/foodmythbuster
PIPELINE_DIR := pipelines/foodmythbuster

# This variable fixes both the path issues and the "unterminated string" (quote) issues
LOCAL_CONFIG := DUCKDB_PATH="data/foodmythbuster.duckdb" DATA_WRITER__LOADER_FILE_FORMAT="parquet"

.PHONY: dev dev-global clean

# ... keep help/install/infra targets as they were ...

ingest:
	mkdir -p data
	$(LOCAL_CONFIG) bruin run $(PIPELINE_DIR)/assets/off_brazil_products.py

build:
	mkdir -p data
	$(LOCAL_CONFIG) bruin run $(PIPELINE_DIR)/assets/off_brazil_products.py
	$(LOCAL_CONFIG) bruin run $(PIPELINE_DIR)/assets/dbt_build.py

dev:
	mkdir -p data
	FOODMYTHBUSTER_TARGET=duckdb $(LOCAL_CONFIG) bruin run $(PIPELINE_DIR)/assets/off_brazil_products.py
	FOODMYTHBUSTER_TARGET=duckdb $(LOCAL_CONFIG) bruin run $(PIPELINE_DIR)/assets/dbt_build.py
	FOODMYTHBUSTER_BACKEND=duckdb $(LOCAL_CONFIG) streamlit run dashboard/app.py

dev-global:
	mkdir -p data
	FOODMYTHBUSTER_TARGET=duckdb FOODMYTHBUSTER_SCOPE=global $(LOCAL_CONFIG) bruin run $(PIPELINE_DIR)/assets/off_brazil_products.py
	FOODMYTHBUSTER_TARGET=duckdb $(LOCAL_CONFIG) bruin run $(PIPELINE_DIR)/assets/dbt_build.py
	FOODMYTHBUSTER_BACKEND=duckdb $(LOCAL_CONFIG) streamlit run dashboard/app.py

clean:
	rm -rf $(DBT_DIR)/target $(DBT_DIR)/logs logs/