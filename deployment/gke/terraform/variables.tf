# GKE Cluster Management - Terraform Variables
# Systematic infrastructure configuration for Beast Mode GKE clusters

variable "project_id" {
  description = "GCP project ID for cluster deployment"
  type        = string
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
  default     = "beast-mode-cluster"
}

variable "region" {
  description = "GCP region for cluster deployment"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

# Node Pool Configuration
variable "machine_type" {
  description = "Machine type for cluster nodes"
  type        = string
  default     = "e2-standard-2"
}

variable "min_nodes" {
  description = "Minimum number of nodes per zone"
  type        = number
  default     = 1
}

variable "max_nodes" {
  description = "Maximum number of nodes per zone"
  type        = number
  default     = 3
}

variable "disk_size_gb" {
  description = "Disk size for cluster nodes in GB"
  type        = number
  default     = 50
}

variable "disk_type" {
  description = "Disk type for cluster nodes"
  type        = string
  default     = "pd-standard"
}

# Network Configuration
variable "network_name" {
  description = "Name of the VPC network"
  type        = string
  default     = "beast-mode-network"
}

variable "subnet_name" {
  description = "Name of the subnet"
  type        = string
  default     = "beast-mode-subnet"
}

variable "subnet_cidr" {
  description = "CIDR range for the subnet"
  type        = string
  default     = "10.0.0.0/24"
}

variable "pods_cidr" {
  description = "CIDR range for pods"
  type        = string
  default     = "10.1.0.0/16"
}

variable "services_cidr" {
  description = "CIDR range for services"
  type        = string
  default     = "10.2.0.0/16"
}

# Security Configuration
variable "enable_workload_identity" {
  description = "Enable Workload Identity for secure GCP service integration"
  type        = bool
  default     = true
}

variable "enable_network_policy" {
  description = "Enable network policy for pod-to-pod traffic control"
  type        = bool
  default     = true
}

variable "enable_private_nodes" {
  description = "Enable private nodes (no external IP)"
  type        = bool
  default     = true
}

variable "master_ipv4_cidr_block" {
  description = "CIDR block for the master network"
  type        = string
  default     = "172.16.0.0/28"
}

# Operational Configuration
variable "enable_autoscaling" {
  description = "Enable cluster autoscaling"
  type        = bool
  default     = true
}

variable "enable_autorepair" {
  description = "Enable automatic node repair"
  type        = bool
  default     = true
}

variable "enable_autoupgrade" {
  description = "Enable automatic node upgrades"
  type        = bool
  default     = true
}

variable "kubernetes_version" {
  description = "Kubernetes version for the cluster"
  type        = string
  default     = "latest"
}

variable "maintenance_start_time" {
  description = "Start time for maintenance window (HH:MM format)"
  type        = string
  default     = "03:00"
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable Cloud Monitoring integration"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable Cloud Logging integration"
  type        = bool
  default     = true
}

# Cost Optimization
variable "preemptible_nodes" {
  description = "Use preemptible nodes for cost optimization"
  type        = bool
  default     = false
}

variable "spot_nodes" {
  description = "Use spot instances for cost optimization"
  type        = bool
  default     = false
}

# Labels and Tags
variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    project     = "beast-mode"
    managed-by  = "terraform"
    framework   = "systematic-pdca"
  }
}

variable "node_labels" {
  description = "Labels to apply to cluster nodes"
  type        = map(string)
  default = {
    workload-type = "systematic-pdca"
    cost-center   = "development"
  }
}

# Service Account Configuration
variable "service_account_name" {
  description = "Name of the service account for cluster nodes"
  type        = string
  default     = "beast-mode-cluster-sa"
}

variable "service_account_scopes" {
  description = "OAuth scopes for the service account"
  type        = list(string)
  default = [
    "https://www.googleapis.com/auth/cloud-platform"
  ]
}