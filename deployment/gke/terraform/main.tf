# GKE Cluster Management - Main Terraform Configuration
# Systematic GKE cluster provisioning with enterprise-grade security and operations

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Data sources for project information
data "google_project" "project" {
  project_id = var.project_id
}

data "google_client_config" "default" {}

# VPC Network for systematic isolation
resource "google_compute_network" "beast_mode_network" {
  name                    = var.network_name
  auto_create_subnetworks = false
  description             = "Beast Mode systematic network for GKE cluster"
  
  # Enable systematic network features
  routing_mode = "REGIONAL"
  
  # Apply systematic labels
  labels = merge(var.labels, {
    component = "networking"
    purpose   = "gke-cluster"
  })
}

# Subnet for GKE cluster with systematic CIDR planning
resource "google_compute_subnetwork" "beast_mode_subnet" {
  name          = var.subnet_name
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.beast_mode_network.id
  description   = "Beast Mode systematic subnet for GKE nodes"
  
  # Secondary IP ranges for pods and services (systematic IP planning)
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr
  }
  
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr
  }
  
  # Enable private Google access for systematic security
  private_ip_google_access = true
  
  # Enable flow logs for systematic monitoring
  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Cloud Router for systematic NAT gateway
resource "google_compute_router" "beast_mode_router" {
  name    = "${var.cluster_name}-router"
  region  = var.region
  network = google_compute_network.beast_mode_network.id
  
  description = "Beast Mode systematic router for NAT gateway"
}

# Cloud NAT for systematic outbound connectivity from private nodes
resource "google_compute_router_nat" "beast_mode_nat" {
  name   = "${var.cluster_name}-nat"
  router = google_compute_router.beast_mode_router.name
  region = var.region
  
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Service Account for systematic GKE node identity
resource "google_service_account" "gke_service_account" {
  account_id   = var.service_account_name
  display_name = "Beast Mode GKE Cluster Service Account"
  description  = "Systematic service account for GKE cluster nodes with least-privilege access"
}

# Systematic IAM bindings for GKE service account
resource "google_project_iam_member" "gke_service_account_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_service_account.email}"
}

# GKE Cluster with systematic configuration
resource "google_container_cluster" "beast_mode_cluster" {
  provider = google-beta
  
  name     = var.cluster_name
  location = var.region
  
  description = "Beast Mode systematic GKE cluster for PDCA orchestration"
  
  # Systematic cluster configuration
  min_master_version = var.kubernetes_version == "latest" ? null : var.kubernetes_version
  
  # Remove default node pool (we'll create systematic node pools)
  remove_default_node_pool = true
  initial_node_count       = 1
  
  # Network configuration for systematic isolation
  network    = google_compute_network.beast_mode_network.name
  subnetwork = google_compute_subnetwork.beast_mode_subnet.name
  
  # IP allocation policy for systematic CIDR management
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }
  
  # Private cluster configuration for systematic security
  private_cluster_config {
    enable_private_nodes    = var.enable_private_nodes
    enable_private_endpoint = false  # Keep public endpoint for management
    master_ipv4_cidr_block  = var.master_ipv4_cidr_block
    
    master_global_access_config {
      enabled = true  # Allow global access for systematic management
    }
  }
  
  # Workload Identity for systematic GCP service integration
  workload_identity_config {
    workload_pool = var.enable_workload_identity ? "${var.project_id}.svc.id.goog" : null
  }
  
  # Network policy for systematic pod-to-pod security
  network_policy {
    enabled  = var.enable_network_policy
    provider = var.enable_network_policy ? "CALICO" : null
  }
  
  # Addons configuration for systematic operations
  addons_config {
    http_load_balancing {
      disabled = false
    }
    
    horizontal_pod_autoscaling {
      disabled = false
    }
    
    network_policy_config {
      disabled = !var.enable_network_policy
    }
    
    dns_cache_config {
      enabled = true
    }
    
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }
  }
  
  # Systematic monitoring and logging
  logging_service    = var.enable_logging ? "logging.googleapis.com/kubernetes" : "none"
  monitoring_service = var.enable_monitoring ? "monitoring.googleapis.com/kubernetes" : "none"
  
  # Maintenance policy for systematic updates
  maintenance_policy {
    daily_maintenance_window {
      start_time = var.maintenance_start_time
    }
  }
  
  # Master authentication for systematic security
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
  
  # Resource labels for systematic organization
  resource_labels = merge(var.labels, {
    cluster-name = var.cluster_name
    environment  = var.environment
  })
  
  # Lifecycle management
  lifecycle {
    ignore_changes = [
      # Ignore node pool changes (managed separately)
      node_pool,
      initial_node_count,
    ]
  }
  
  depends_on = [
    google_project_iam_member.gke_service_account_roles,
    google_compute_subnetwork.beast_mode_subnet,
  ]
}

# Systematic node pool for Beast Mode workloads
resource "google_container_node_pool" "beast_mode_nodes" {
  provider = google-beta
  
  name       = "${var.cluster_name}-nodes"
  location   = var.region
  cluster    = google_container_cluster.beast_mode_cluster.name
  
  # Systematic node count and autoscaling
  initial_node_count = var.min_nodes
  
  autoscaling {
    min_node_count = var.min_nodes
    max_node_count = var.max_nodes
  }
  
  # Systematic node configuration
  node_config {
    preemptible  = var.preemptible_nodes
    spot         = var.spot_nodes
    machine_type = var.machine_type
    
    # Systematic disk configuration
    disk_size_gb = var.disk_size_gb
    disk_type    = var.disk_type
    
    # Service account with systematic permissions
    service_account = google_service_account.gke_service_account.email
    oauth_scopes    = var.service_account_scopes
    
    # Systematic node labels
    labels = merge(var.node_labels, {
      cluster-name = var.cluster_name
      environment  = var.environment
      node-pool    = "${var.cluster_name}-nodes"
    })
    
    # Systematic node tags for firewall rules
    tags = [
      "gke-node",
      "beast-mode-cluster",
      var.environment
    ]
    
    # Workload Identity configuration
    workload_metadata_config {
      mode = var.enable_workload_identity ? "GKE_METADATA" : "GCE_METADATA"
    }
    
    # Systematic security configuration
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
    
    # Systematic metadata
    metadata = {
      disable-legacy-endpoints = "true"
    }
  }
  
  # Systematic node management
  management {
    auto_repair  = var.enable_autorepair
    auto_upgrade = var.enable_autoupgrade
  }
  
  # Systematic upgrade settings
  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
  
  depends_on = [
    google_container_cluster.beast_mode_cluster,
  ]
}

# Firewall rule for systematic node communication
resource "google_compute_firewall" "allow_gke_nodes" {
  name    = "${var.cluster_name}-allow-nodes"
  network = google_compute_network.beast_mode_network.name
  
  description = "Allow systematic communication between GKE nodes"
  
  allow {
    protocol = "tcp"
    ports    = ["1-65535"]
  }
  
  allow {
    protocol = "udp"
    ports    = ["1-65535"]
  }
  
  allow {
    protocol = "icmp"
  }
  
  source_tags = ["gke-node"]
  target_tags = ["gke-node"]
}

# Firewall rule for systematic master to nodes communication
resource "google_compute_firewall" "allow_gke_master" {
  name    = "${var.cluster_name}-allow-master"
  network = google_compute_network.beast_mode_network.name
  
  description = "Allow systematic communication from GKE master to nodes"
  
  allow {
    protocol = "tcp"
    ports    = ["443", "10250"]
  }
  
  source_ranges = [var.master_ipv4_cidr_block]
  target_tags   = ["gke-node"]
}