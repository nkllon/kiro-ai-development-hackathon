# Development Environment Configuration
# Optimized for development workloads with cost efficiency

# Environment
environment = "dev"

# Cluster Configuration
cluster_name = "beast-mode-dev"

# Node Configuration (Cost-optimized for development)
machine_type = "e2-standard-2"
min_nodes    = 1
max_nodes    = 2
disk_size_gb = 30
disk_type    = "pd-standard"

# Cost Optimization for Development
preemptible_nodes = true  # Use preemptible nodes for cost savings
spot_nodes        = false

# Security Configuration (Relaxed for development)
enable_private_nodes = false  # Allow external access for development

# Operational Configuration
maintenance_start_time = "02:00"  # Early morning maintenance

# Labels
labels = {
  project     = "beast-mode"
  managed-by  = "terraform"
  framework   = "systematic-pdca"
  environment = "dev"
  cost-center = "development"
}

node_labels = {
  workload-type = "systematic-pdca"
  cost-center   = "development"
  environment   = "dev"
  node-type     = "preemptible"
}