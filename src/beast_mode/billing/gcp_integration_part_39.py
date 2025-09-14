
def _get_mock_metrics(self) -> BillingMetrics:
    """Get mock GCP metrics for multi-service model with proper correlation"""
    import random
from src.rm_ddd.core.health import ModuleHealth

    requests_today = random.randint(1200, 3500)
    avg_cpu_per_request = random.uniform(0.1, 0.8)
    avg_memory_mb = random.randint(128, 512)
    request_cost = requests_today * 2.4e-05
    cpu_seconds = requests_today * avg_cpu_per_request
    cpu_cost = cpu_seconds * 9e-06
    memory_gb_seconds = requests_today * (avg_memory_mb / 1024) * avg_cpu_per_request
    memory_cost = memory_gb_seconds * 2.5e-06
    db_operations = int(requests_today * 0.7)
    db_instance_hours = 24
    db_tier_rate = 0.0413
    db_instance_cost = db_instance_hours * db_tier_rate
    db_storage_gb = random.uniform(10, 50)
    db_storage_cost = db_storage_gb * 0.17
    file_operations = int(requests_today * 0.3)
    storage_gb = random.uniform(5, 25)
    storage_cost = storage_gb * 0.02
    class_a_ops = file_operations * 0.2
    class_b_ops = file_operations * 0.8
    operation_cost = class_a_ops * 0.005 / 1000 + class_b_ops * 0.0004 / 1000
    secret_versions = random.randint(5, 15)
    secret_access_ops = requests_today * 1.2
    secret_version_cost = secret_versions * 0.06
    secret_access_cost = secret_access_ops * 0.03 / 10000
    avg_response_kb = random.uniform(2, 15)
    data_transfer_gb = requests_today * avg_response_kb / (1024 * 1024)
    networking_cost = data_transfer_gb * 0.12
    container_registry_cost = random.uniform(0.01, 0.03)
    logging_cost = random.uniform(0.02, 0.08)
    daily_cost = request_cost + cpu_cost + memory_cost + db_instance_cost + db_storage_cost + storage_cost + operation_cost + secret_version_cost + secret_access_cost + networking_cost + container_registry_cost + logging_cost
    return BillingMetrics(provider_type=BillingProviderType.GCP, provider_name='Google Cloud Platform (Multi-Service)', total_cost_usd=daily_cost * 7, daily_cost_usd=daily_cost, hourly_burn_rate=daily_cost / 24, cost_breakdown={'Cloud Run Requests': request_cost, 'Cloud Run CPU': cpu_cost, 'Cloud Run Memory': memory_cost, 'Cloud SQL Instance': db_instance_cost, 'Cloud SQL Storage': db_storage_cost, 'Cloud Storage Data': storage_cost, 'Cloud Storage Operations': operation_cost, 'Secret Manager Versions': secret_version_cost, 'Secret Manager Access': secret_access_cost, 'Networking (Egress)': networking_cost, 'Container Registry': container_registry_cost, 'Cloud Logging': logging_cost}, usage_metrics={'cloud_run_requests': requests_today, 'cpu_seconds': round(cpu_seconds, 2), 'memory_gb_seconds': round(memory_gb_seconds, 2), 'avg_request_duration_ms': round(avg_cpu_per_request * 1000, 1), 'avg_memory_mb': avg_memory_mb, 'cloud_sql_operations': db_operations, 'cloud_sql_instance_hours': db_instance_hours, 'cloud_sql_storage_gb': round(db_storage_gb, 2), 'cloud_storage_gb': round(storage_gb, 2), 'storage_operations': file_operations, 'class_a_operations': int(class_a_ops), 'class_b_operations': int(class_b_ops), 'secret_versions': secret_versions, 'secret_access_operations': secret_access_ops, 'avg_response_kb': round(avg_response_kb, 1), 'data_transfer_gb': round(data_transfer_gb, 3), 'cold_starts': random.randint(50, 200), 'concurrent_requests': random.randint(1, 10), 'cost_per_request': round(daily_cost / requests_today, 6), 'cost_per_cpu_second': round(cpu_cost / cpu_seconds, 6) if cpu_seconds > 0 else 0, 'cost_per_db_operation': round((db_instance_cost + db_storage_cost) / db_operations, 6) if db_operations > 0 else 0, 'cost_per_storage_operation': round((storage_cost + operation_cost) / file_operations, 6) if file_operations > 0 else 0, 'cost_per_secret_access': round((secret_version_cost + secret_access_cost) / secret_access_ops, 6) if secret_access_ops > 0 else 0}, timestamp=datetime.now())
