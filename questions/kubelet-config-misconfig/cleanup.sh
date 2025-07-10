#!/bin/bash

# Cleanup script for CKA practice question: Kubelet Configuration Misconfiguration

# Variables
NODE_NAME="node01"
PRACTICE_DIR="/opt/practice"
CONFIG_FILE="/var/lib/kubelet/config.yaml"
BACKUP_FILE="${PRACTICE_DIR}/config.yaml.bak"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed.${NC}"
    exit 1
fi

# Restore original config on node
ssh ${NODE_NAME} "sudo cp ${BACKUP_FILE} ${CONFIG_FILE}"
ssh ${NODE_NAME} "sudo systemctl restart kubelet"

# Remove practice directory and files
echo "Removing practice directory and files..."
sudo rm -rf ${PRACTICE_DIR}

echo -e "${GREEN}Cleanup complete. All resources have been removed.${NC}"