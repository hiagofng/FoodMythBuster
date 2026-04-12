variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for GCS and BigQuery"
  type        = string
  default     = "southamerica-east1"
}

variable "dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
  default     = "foodmythbuster"
}

variable "bucket_name_suffix" {
  description = "Unique suffix for the GCS bucket (full name = foodmythbuster-raw-<suffix>)"
  type        = string
}

variable "service_account_id" {
  description = "Pipeline service account short ID"
  type        = string
  default     = "foodmythbuster-pipeline"
}

variable "user_email" {
  description = "Your gcloud user email — granted serviceAccountTokenCreator so you can impersonate the pipeline SA locally. Leave empty to skip."
  type        = string
  default     = ""
}
