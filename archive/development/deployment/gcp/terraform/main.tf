# Research CMA System - GCP Infrastructure as Code
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "sql-component.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com"
  ])
  
  service = each.value
  disable_on_destroy = false
}

# Cloud SQL PostgreSQL instance
resource "google_sql_database_instance" "research_cms_db" {
  name             = "research-cms-db-${var.environment}"
  database_version = "POSTGRES_14"
  region           = var.region
  deletion_protection = false

  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled = true
      start_time = "03:00"
      point_in_time_recovery_enabled = true
    }
    
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
    
    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Database
resource "google_sql_database" "research_cms" {
  name     = "research_cms"
  instance = google_sql_database_instance.research_cms_db.name
}

# Database user
resource "google_sql_user" "research_cms_user" {
  name     = "research_cms"
  instance = google_sql_database_instance.research_cms_db.name
  password = random_password.db_password.result
}

# Generate random password for database
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store database password in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "research-cms-db-password"
  
  replication {
    automatic = true
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Cloud Storage bucket for documents
resource "google_storage_bucket" "research_cms_documents" {
  name     = "${var.project_id}-research-cms-documents-${var.environment}"
  location = var.region
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}

# Service account for Cloud Run
resource "google_service_account" "research_cms" {
  account_id   = "research-cms-${var.environment}"
  display_name = "Research CMS Service Account"
  description  = "Service account for Research CMS Cloud Run service"
}

# IAM bindings for service account
resource "google_project_iam_member" "research_cms_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.research_cms.email}"
}

resource "google_project_iam_member" "research_cms_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.research_cms.email}"
}

resource "google_project_iam_member" "research_cms_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.research_cms.email}"
}

# Cloud Run service
resource "google_cloud_run_service" "research_cms" {
  name     = "research-cms-${var.environment}"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.research_cms.email
      
      containers {
        image = "gcr.io/${var.project_id}/research-cms:latest"
        
        ports {
          container_port = 8080
        }
        
        resources {
          limits = {
            cpu    = "2000m"
            memory = "2Gi"
          }
        }
        
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        env {
          name  = "DB_HOST"
          value = google_sql_database_instance.research_cms_db.private_ip_address
        }
        
        env {
          name  = "DB_NAME"
          value = google_sql_database.research_cms.name
        }
        
        env {
          name  = "DB_USER"
          value = google_sql_user.research_cms_user.name
        }
        
        env {
          name = "DB_PASSWORD"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_password.secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name  = "STORAGE_BUCKET"
          value = google_storage_bucket.research_cms_documents.name
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "100"
        "autoscaling.knative.dev/minScale" = "0"
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.research_cms_db.connection_name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.required_apis]
}

# Make Cloud Run service publicly accessible
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.research_cms.name
  location = google_cloud_run_service.research_cms.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "service_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_service.research_cms.status[0].url
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.research_cms_db.connection_name
}

output "storage_bucket_name" {
  description = "Cloud Storage bucket name"
  value       = google_storage_bucket.research_cms_documents.name
}