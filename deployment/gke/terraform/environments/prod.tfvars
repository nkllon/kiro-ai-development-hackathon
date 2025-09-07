# Production Environment Configuration
# Optimized for production workloads with high availability and security

# Environment
environment = "prod"

# Cluster Configuration
cluster_name = "beast-mode-prod"

# Node Configuration (Production-grade)
machine_type = "e2-standard-4"
min_nodes    = 2
max_nodes    = 10
disk_size_gb = 100
disk_type    = "pd-ssd"

# Cost Optimization for Production
preemptible_nodes = false  # No preemptible nodes in production
spot_nodes        = false

# Security Configuration (Maximum security for production)
enable_private_nodes     = true
enable_network_policy    = true
enable_workload_identity = true

# Operational Configuration
maintenance_start_time = "03:00"  # Low-traffic maintenance window

# Labels
labels = {
  project     = "beast-mode"
  managed-by  = "terraform"
  framework   = "systematic-pdca"
  environment = "prod"
  cost-center = "production"
  criticality = "high"
}

node_labels = {
  workload-type = "systematic-pdca"
  cost-center   = "production"
  environment   = "prod"
  node-type     = "standard"
  criticality   = "high"
}