output "bucket_name" {
  description = "Raw data-lake GCS bucket"
  value       = google_storage_bucket.raw.name
}

output "dataset_id" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.main.dataset_id
}

output "service_account_email" {
  description = "Pipeline service account email"
  value       = google_service_account.pipeline.email
}
