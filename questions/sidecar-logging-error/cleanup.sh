#!/bin/bash

# Cleanup script for CKA practice question: Sidecar Logging Configuration Error

# Variables
NAMESPACE="sidecar-ns"
POD_NAME="logging-pod"
PRACTICE_DIR="/opt/practice"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed.${NC}"
    exit 1
fi

# Delete pod
kubectl -n ${NAMESPACE} delete pod ${POD_NAME} --ignore-not-found

# Delete namespace
kubectl delete namespace ${NAMESPACE} --ignore-not-found

# Remove practice directory and files
echo "Removing practice directory and files..."
sudo rm -rf ${PRACTICE_DIR}

echo -e "${GREEN}Cleanup complete. All resources have been removed.${NC}"