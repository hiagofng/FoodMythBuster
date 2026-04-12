# APIs ------------------------------------------------------------------------
resource "google_project_service" "apis" {
  for_each = toset([
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "bigquerystorage.googleapis.com",
    "iam.googleapis.com",
  ])
  service            = each.key
  disable_on_destroy = false
}

# Raw data-lake bucket --------------------------------------------------------
resource "google_storage_bucket" "raw" {
  name                        = "foodmythbuster-raw-${var.bucket_name_suffix}"
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = false

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  depends_on = [google_project_service.apis]
}

# BigQuery dataset ------------------------------------------------------------
resource "google_bigquery_dataset" "main" {
  dataset_id                 = var.dataset_id
  location                   = var.region
  delete_contents_on_destroy = false

  depends_on = [google_project_service.apis]
}

# Pipeline service account ----------------------------------------------------
resource "google_service_account" "pipeline" {
  account_id   = var.service_account_id
  display_name = "FoodMythBuster pipeline"
  depends_on   = [google_project_service.apis]
}

resource "google_storage_bucket_iam_member" "sa_bucket" {
  bucket = google_storage_bucket.raw.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_bigquery_dataset_iam_member" "sa_dataset" {
  dataset_id = google_bigquery_dataset.main.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_project_iam_member" "sa_bq_jobuser" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline.email}"
}

# Allow the human user to impersonate the pipeline SA. This is the
# key-less alternative when iam.disableServiceAccountKeyCreation is
# enforced by org policy. Set var.user_email to your gcloud identity.
resource "google_service_account_iam_member" "user_can_impersonate" {
  count              = var.user_email == "" ? 0 : 1
  service_account_id = google_service_account.pipeline.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "user:${var.user_email}"
}
