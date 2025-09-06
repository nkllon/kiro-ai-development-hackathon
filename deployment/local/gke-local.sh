#!/bin/bash
# GKE Local Development - Minikube with GCP Integration
# Runs GKE-compatible Kubernetes locally with Google Cloud services

set -e

echo "☸️  GKE Local Development Mode"
echo "Using Minikube with GCP service integration"
echo "============================================="

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "📦 Installing Minikube..."
    # macOS installation
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install minikube
        else
            curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
            sudo install minikube-darwin-amd64 /usr/local/bin/minikube
        fi
    else
        echo "❌ Please install Minikube manually for your OS"
        exit 1
    fi
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "📦 Installing kubectl..."
    if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &> /dev/null; then
        brew install kubectl
    else
        echo "❌ Please install kubectl manually"
        exit 1
    fi
fi

# Start Minikube with GKE-like configuration
echo "🚀 Starting Minikube with GKE-compatible configuration..."
minikube start \
    --driver=docker \
    --cpus=4 \
    --memory=8192 \
    --disk-size=20g \
    --kubernetes-version=v1.28.0 \
    --addons=ingress,metrics-server,dashboard \
    --profile=systematic-pdca

# Enable GCP-like features
echo "🔧 Configuring GKE-like features..."
minikube addons enable ingress -p systematic-pdca
minikube addons enable metrics-server -p systematic-pdca

# Set kubectl context
kubectl config use-context systematic-pdca

# Create namespace
echo "📦 Creating namespace..."
kubectl create namespace systematic-pdca || echo "Namespace may already exist"

# Build image locally and load into Minikube
echo "🏗️  Building and loading container image..."
eval $(minikube docker-env -p systematic-pdca)
docker build -f deployment/systematic-pdca/Dockerfile -t systematic-pdca-orchestrator:local .

# Create local Kubernetes manifests (simplified for local dev)
echo "📦 Creating local Kubernetes manifests..."
cat > /tmp/local-k8s-manifests.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: systematic-pdca-config
  namespace: systematic-pdca
data:
  ENVIRONMENT: "development"
  PYTHONPATH: "/app"
  LOG_LEVEL: "DEBUG"
  PORT: "8080"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: systematic-pdca-orchestrator
  namespace: systematic-pdca
  labels:
    app: systematic-pdca-orchestrator
spec:
  replicas: 1  # Single replica for local dev
  selector:
    matchLabels:
      app: systematic-pdca-orchestrator
  template:
    metadata:
      labels:
        app: systematic-pdca-orchestrator
    spec:
      containers:
      - name: systematic-pdca-orchestrator
        image: systematic-pdca-orchestrator:local
        imagePullPolicy: Never  # Use local image
        ports:
        - containerPort: 8080
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
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
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

---
apiVersion: v1
kind: Service
metadata:
  name: systematic-pdca-service
  namespace: systematic-pdca
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080
  selector:
    app: systematic-pdca-orchestrator
EOF

# Deploy to local Minikube
echo "📦 Deploying to local Minikube..."
kubectl apply -f /tmp/local-k8s-manifests.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/systematic-pdca-orchestrator -n systematic-pdca

# Get service URL
MINIKUBE_IP=$(minikube ip -p systematic-pdca)
SERVICE_URL="http://$MINIKUBE_IP:30080"

echo ""
echo "🎉 Local GKE Development Environment Ready!"
echo "============================================="
echo "Minikube Profile: systematic-pdca"
echo "Service URL: $SERVICE_URL"
echo "Kubernetes Dashboard: minikube dashboard -p systematic-pdca"
echo ""
echo "🧪 Test the local deployment:"
echo "curl $SERVICE_URL/health"
echo "curl $SERVICE_URL/domains"
echo ""
echo "🔍 Useful commands:"
echo "kubectl get pods -n systematic-pdca"
echo "kubectl logs -f deployment/systematic-pdca-orchestrator -n systematic-pdca"
echo "minikube service systematic-pdca-service -n systematic-pdca -p systematic-pdca"
echo ""
echo "🛑 Stop local environment:"
echo "minikube stop -p systematic-pdca"
echo "minikube delete -p systematic-pdca"

# Clean up temp file
rm -f /tmp/local-k8s-manifests.yaml