#!/bin/bash

# Setup script for CKA practice question: CronJob Curling Nginx Service Not Working

# Variables
NAMESPACE="default"  # Using default namespace as per your example
POD_NAME="pod1"
SERVICE_NAME="nginx-svc"
CRONJOB_NAME="curl-cron"
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

# Create Nginx pod
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: ${POD_NAME}
  namespace: ${NAMESPACE}
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
EOF

# Create service exposing the pod
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: ${SERVICE_NAME}
  namespace: ${NAMESPACE}
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
EOF

# Create CronJob with wrong command (curl pod1 instead of service)
cat << EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ${CRONJOB_NAME}
  namespace: ${NAMESPACE}
spec:
  schedule: "* * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: curl-job
            image: curlimages/curl:latest
            command: ["curl", "${POD_NAME}"]
          restartPolicy: OnFailure
EOF

# Wait for initial job creation (up to 60 seconds)
echo "Waiting for initial job creation..."
timeout 60 bash -c "until kubectl -n ${NAMESPACE} get jobs --selector=job-name=${CRONJOB_NAME}-* &> /dev/null; do sleep 5; done"

# Output the practice question
echo -e "\n${GREEN}=== CKA Practice Question ===${NC}"
echo "Troubleshoot why the CronJob '${CRONJOB_NAME}' in namespace '${NAMESPACE}', which is supposed to curl an Nginx service every minute, is not working (jobs are failing)."
echo "Diagnose via logs, fix the command to curl the correct service DNS ('${SERVICE_NAME}.${NAMESPACE}.svc.cluster.local'), and ensure curls succeed."
echo -e "\n${GREEN}Setup complete. You can now attempt the practice question.${NC}"