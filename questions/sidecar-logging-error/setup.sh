#!/bin/bash

# Setup script for CKA practice question: Sidecar Logging Configuration Error

# Variables
NAMESPACE="sidecar-ns"
POD_NAME="logging-pod"
PRACTICE_DIR="/opt/practice"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if running on master node
if ! kubectl get nodes | grep -q "control-plane"; then
    echo -e "${RED}Error: This script must be run on the Kubernetes master node.${NC}"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed. Please install kubectl and configure it to access the cluster.${NC}"
    exit 1
fi

# Create practice directory
sudo mkdir -p ${PRACTICE_DIR}
sudo chmod 777 ${PRACTICE_DIR}

# Create namespace
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Create pod with main nginx and misconfigured logging sidecar (wrong mount path)
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: ${POD_NAME}
  namespace: ${NAMESPACE}
spec:
  volumes:
  - name: logs-volume
    emptyDir: {}
  containers:
  - name: nginx
    image: nginx:latest
    volumeMounts:
    - name: logs-volume
      mountPath: /var/log/nginx
  - name: logger
    image: busybox:latest
    command: ["/bin/sh", "-c", "tail -f /wrong/path/access.log"]
    volumeMounts:
    - name: logs-volume
      mountPath: /wrong/path  # Misconfigured path
EOF

# Wait for pod to be running (up to 60 seconds)
echo "Waiting for pod to be running..."
kubectl -n ${NAMESPACE} wait --for=condition=Ready pod/${POD_NAME} --timeout=60s

# Output the practice question
echo -e "\n${GREEN}=== CKA Practice Question ===${NC}"
echo "Troubleshoot why the logging sidecar in pod '${POD_NAME}' in namespace '${NAMESPACE}' is not collecting logs from the main nginx container."
echo "Fix the sidecar's volume mount path to '/var/log/nginx', and verify logs are being tailed by checking the sidecar logs."
echo -e "\n${GREEN}Setup complete. You can now attempt the practice question.${NC}"