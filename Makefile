# FoodMythBuster — one-command runners
# Usage: `make all` for a full cloud run, or `make dev` for local DuckDB.

SHELL := /bin/bash

# Auto-load .env if present so targets don't need inline exports.
ifneq (,$(wildcard .env))
    include .env
    export
endif

DBT_DIR := dbt/foodmythbuster
INFRA_DIR := infra
PIPELINE_DIR := pipelines/foodmythbuster

.PHONY: help install infra infra-destroy ingest transform test build dashboard all dev clean

help:
	@echo "FoodMythBuster targets:"
	@echo "  install         pip install -r requirements.txt"
	@echo "  infra           terraform apply (GCS + BigQuery + SA + IAM)"
	@echo "  infra-destroy   terraform destroy"
	@echo "  ingest          dlt: Open Food Facts -> raw table"
	@echo "  transform       dbt build (staging + marts + tests)"
	@echo "  test            dbt test only"
	@echo "  build           Bruin runs the full DAG (ingest + transform)"
	@echo "  dashboard       streamlit run dashboard/app.py"
	@echo "  all             infra + build + dashboard (cloud, one shot)"
	@echo "  dev             local DuckDB end-to-end (no cloud)"
	@echo "  clean           remove dbt target/ and logs/"

install:
	pip install -r requirements.txt

infra:
	cd $(INFRA_DIR) && terraform init && terraform apply -auto-approve

infra-destroy:
	cd $(INFRA_DIR) && terraform destroy

ingest:
	bruin run $(PIPELINE_DIR)/assets/off_brazil_products.py

transform:
	cd $(DBT_DIR) && DBT_PROFILES_DIR=. dbt build

test:
	cd $(DBT_DIR) && DBT_PROFILES_DIR=. dbt test

build:
	bruin run $(PIPELINE_DIR)

dashboard:
	streamlit run dashboard/app.py

all: infra build dashboard

dev:
	FOODMYTHBUSTER_TARGET=duckdb bruin run $(PIPELINE_DIR)/assets/off_brazil_products.py
	FOODMYTHBUSTER_TARGET=duckdb bruin run $(PIPELINE_DIR)/assets/stg_products_duckdb.sql
	FOODMYTHBUSTER_BACKEND=duckdb streamlit run dashboard/app.py

clean:
	rm -rf $(DBT_DIR)/target $(DBT_DIR)/logs logs/
