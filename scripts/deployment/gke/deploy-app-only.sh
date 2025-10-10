#!/bin/bash
# Systematic PDCA Orchestrator - Application-Only GKE Deployment
# Assumes GKE cluster already exists and is managed separately

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
CLUSTER_NAME=${2:-"existing-cluster"}
REGION=${3:-"us-central1"}
DOMAIN=${4:-"YOUR_DOMAIN.com"}
NAMESPACE=${5:-"systematic-pdca"}

echo "🚀 Deploying Systematic PDCA Orchestrator to Existing GKE Cluster"
echo "Project: $PROJECT_ID"
echo "Cluster: $CLUSTER_NAME (existing)"
echo "Region: $REGION"
echo "Domain: $DOMAIN"
echo "Namespace: $NAMESPACE"
echo "=============================================================="

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

# Set the project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Get cluster credentials
echo "🔑 Getting cluster credentials..."
if ! gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION; then
    echo "❌ Failed to get cluster credentials. Ensure cluster exists and you have access."
    exit 1
fi

# Verify cluster access
echo "🔍 Verifying cluster access..."
if ! kubectl cluster-info &>/dev/null; then
    echo "❌ Cannot access Kubernetes cluster. Check your credentials and cluster status."
    exit 1
fi

echo "✅ Successfully connected to cluster: $CLUSTER_NAME"

# Create service account for Workload Identity (if not exists)
echo "🔐 Setting up Workload Identity..."
gcloud iam service-accounts create systematic-pdca \
    --display-name="Systematic PDCA Orchestrator Service Account" || echo "Service account may already exist"

# Grant minimal IAM permissions
echo "🛡️  Granting IAM permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:systematic-pdca@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:systematic-pdca@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/monitoring.metricWriter"

# Create namespace
echo "📦 Creating namespace..."
kubectl create namespace $NAMESPACE || echo "Namespace may already exist"

# Create Kubernetes service account
kubectl create serviceaccount systematic-pdca-sa \
    --namespace $NAMESPACE || echo "Service account may already exist"

# Bind Kubernetes service account to Google service account
gcloud iam service-accounts add-iam-policy-binding \
    systematic-pdca@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[$NAMESPACE/systematic-pdca-sa]"

kubectl annotate serviceaccount systematic-pdca-sa \
    --namespace $NAMESPACE \
    iam.gke.io/gcp-service-account=systematic-pdca@$PROJECT_ID.iam.gserviceaccount.com \
    --overwrite

# Build and push container image
echo "🏗️  Building and pushing container image..."
gcloud builds submit --config=deployment/systematic-pdca/cloudbuild.yaml .

# Create application-only Kubernetes manifests (without cluster resources)
echo "📦 Creating application manifests..."
cat > /tmp/app-only-manifests.yaml << EOF
# ConfigMap for application configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: systematic-pdca-config
  namespace: $NAMESPACE
data:
  ENVIRONMENT: "production"
  PYTHONPATH: "/app"
  LOG_LEVEL: "INFO"
  PORT: "8080"

---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: systematic-pdca-orchestrator
  namespace: $NAMESPACE
  labels:
    app: systematic-pdca-orchestrator
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: systematic-pdca-orchestrator
  template:
    metadata:
      labels:
        app: systematic-pdca-orchestrator
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: systematic-pdca-sa
      containers:
      - name: systematic-pdca-orchestrator
        image: gcr.io/$PROJECT_ID/systematic-pdca-orchestrator:latest
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        env:
        - name: PORT
          value: "8080"
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: systematic-pdca-config
              key: ENVIRONMENT
        - name: PYTHONPATH
          valueFrom:
            configMapKeyRef:
              name: systematic-pdca-config
              key: PYTHONPATH
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        startupProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
          failureThreshold: 30

---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: systematic-pdca-hpa
  namespace: $NAMESPACE
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: systematic-pdca-orchestrator
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

---
# Service
apiVersion: v1
kind: Service
metadata:
  name: systematic-pdca-service
  namespace: $NAMESPACE
  labels:
    app: systematic-pdca-orchestrator
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
  selector:
    app: systematic-pdca-orchestrator

---
# Pod Disruption Budget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: systematic-pdca-pdb
  namespace: $NAMESPACE
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: systematic-pdca-orchestrator
EOF

# Apply application manifests
echo "📦 Deploying application to Kubernetes..."
kubectl apply -f /tmp/app-only-manifests.yaml

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/systematic-pdca-orchestrator -n $NAMESPACE

# Get service information
echo "🔍 Getting service information..."
SERVICE_IP=$(kubectl get service systematic-pdca-service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')

echo ""
echo "🎉 Application Deployment completed successfully!"
echo "=============================================================="
echo "Cluster: $CLUSTER_NAME (existing)"
echo "Namespace: $NAMESPACE"
echo "Service IP: $SERVICE_IP (internal)"
echo "Replicas: 3 (auto-scaling 2-10)"
echo ""
echo "🔍 Useful commands:"
echo "kubectl get pods -n $NAMESPACE"
echo "kubectl logs -f deployment/systematic-pdca-orchestrator -n $NAMESPACE"
echo "kubectl describe hpa systematic-pdca-hpa -n $NAMESPACE"
echo ""
echo "🧪 Test the deployment (from within cluster):"
echo "kubectl run test-pod --rm -i --tty --image=curlimages/curl -- curl http://systematic-pdca-service.$NAMESPACE.svc.cluster.local/health"
echo ""
echo "📊 Monitor with:"
echo "kubectl top pods -n $NAMESPACE"
echo "kubectl get hpa -n $NAMESPACE"
echo ""
echo "🎯 Systematic PDCA Orchestrator is now running on existing GKE cluster with:"
echo "  ✅ Application-only deployment (no cluster management)"
echo "  ✅ High availability (3 replicas)"
echo "  ✅ Auto-scaling (2-10 pods)"
echo "  ✅ Workload Identity (secure GCP integration)"
echo "  ✅ Resource optimization (requests/limits)"
echo ""
echo "💡 Note: This deployment assumes cluster networking and ingress are managed separately."
echo "    Contact your cluster administrator for external access configuration."

# Clean up temp file
rm -f /tmp/app-only-manifests.yaml