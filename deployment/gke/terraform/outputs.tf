# GKE Cluster Management - Terraform Outputs
# Systematic output values for cluster integration and operations

# Cluster Information
output "cluster_name" {
  description = "Name of the GKE cluster"
  value       = google_container_cluster.beast_mode_cluster.name
}

output "cluster_location" {
  description = "Location of the GKE cluster"
  value       = google_container_cluster.beast_mode_cluster.location
}

output "cluster_endpoint" {
  description = "Endpoint for the GKE cluster API server"
  value       = google_container_cluster.beast_mode_cluster.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "Base64 encoded CA certificate for the cluster"
  value       = google_container_cluster.beast_mode_cluster.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "cluster_version" {
  description = "Current Kubernetes version of the cluster"
  value       = google_container_cluster.beast_mode_cluster.master_version
}

# Network Information
output "network_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.beast_mode_network.name
}

output "network_self_link" {
  description = "Self-link of the VPC network"
  value       = google_compute_network.beast_mode_network.self_link
}

output "subnet_name" {
  description = "Name of the subnet"
  value       = google_compute_subnetwork.beast_mode_subnet.name
}

output "subnet_self_link" {
  description = "Self-link of the subnet"
  value       = google_compute_subnetwork.beast_mode_subnet.self_link
}

output "subnet_cidr" {
  description = "CIDR range of the subnet"
  value       = google_compute_subnetwork.beast_mode_subnet.ip_cidr_range
}

output "pods_cidr" {
  description = "CIDR range for pods"
  value       = var.pods_cidr
}

output "services_cidr" {
  description = "CIDR range for services"
  value       = var.services_cidr
}

# Service Account Information
output "service_account_email" {
  description = "Email of the GKE service account"
  value       = google_service_account.gke_service_account.email
}

output "service_account_name" {
  description = "Name of the GKE service account"
  value       = google_service_account.gke_service_account.name
}

# Node Pool Information
output "node_pool_name" {
  description = "Name of the primary node pool"
  value       = google_container_node_pool.beast_mode_nodes.name
}

output "node_pool_instance_group_urls" {
  description = "Instance group URLs of the node pool"
  value       = google_container_node_pool.beast_mode_nodes.instance_group_urls
}

# Workload Identity Information
output "workload_identity_enabled" {
  description = "Whether Workload Identity is enabled"
  value       = var.enable_workload_identity
}

output "workload_pool" {
  description = "Workload Identity pool for the cluster"
  value       = var.enable_workload_identity ? "${var.project_id}.svc.id.goog" : null
}

# Security Configuration
output "private_nodes_enabled" {
  description = "Whether private nodes are enabled"
  value       = var.enable_private_nodes
}

output "network_policy_enabled" {
  description = "Whether network policy is enabled"
  value       = var.enable_network_policy
}

output "master_ipv4_cidr_block" {
  description = "CIDR block for the master network"
  value       = var.master_ipv4_cidr_block
}

# Operational Configuration
output "monitoring_enabled" {
  description = "Whether Cloud Monitoring is enabled"
  value       = var.enable_monitoring
}

output "logging_enabled" {
  description = "Whether Cloud Logging is enabled"
  value       = var.enable_logging
}

output "autoscaling_enabled" {
  description = "Whether cluster autoscaling is enabled"
  value       = var.enable_autoscaling
}

# kubectl Configuration Command
output "kubectl_config_command" {
  description = "Command to configure kubectl for this cluster"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.beast_mode_cluster.name} --region ${google_container_cluster.beast_mode_cluster.location} --project ${var.project_id}"
}

# Cluster Access Information
output "cluster_access_info" {
  description = "Information for accessing the cluster"
  value = {
    cluster_name = google_container_cluster.beast_mode_cluster.name
    location     = google_container_cluster.beast_mode_cluster.location
    project_id   = var.project_id
    endpoint     = google_container_cluster.beast_mode_cluster.endpoint
  }
  sensitive = true
}

# Cost Optimization Information
output "cost_optimization_info" {
  description = "Cost optimization configuration"
  value = {
    preemptible_nodes = var.preemptible_nodes
    spot_nodes        = var.spot_nodes
    machine_type      = var.machine_type
    min_nodes         = var.min_nodes
    max_nodes         = var.max_nodes
    disk_size_gb      = var.disk_size_gb
    disk_type         = var.disk_type
  }
}

# Systematic Labels
output "cluster_labels" {
  description = "Labels applied to the cluster"
  value       = google_container_cluster.beast_mode_cluster.resource_labels
}

output "node_labels" {
  description = "Labels applied to cluster nodes"
  value       = google_container_node_pool.beast_mode_nodes.node_config[0].labels
}

# Environment Information
output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "region" {
  description = "GCP region"
  value       = var.region
}

output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}