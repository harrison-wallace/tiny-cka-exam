#!/bin/bash

# Setup script for CKA practice question: Kubelet Configuration Misconfiguration

# Variables
NODE_NAME="node01"
PRACTICE_DIR="/opt/practice"
CONFIG_FILE="/var/lib/kubelet/config.yaml"
BACKUP_FILE="${PRACTICE_DIR}/config.yaml.bak"

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

# Assume passwordless SSH to node01 as root or sudo user
if ! ssh ${NODE_NAME} "echo 'SSH access test'" &> /dev/null; then
    echo -e "${RED}Error: Passwordless SSH to ${NODE_NAME} is required.${NC}"
    exit 1
fi

# Create practice directory
sudo mkdir -p ${PRACTICE_DIR}
sudo chmod 777 ${PRACTICE_DIR}

# Backup original config on node
ssh ${NODE_NAME} "sudo cp ${CONFIG_FILE} ${BACKUP_FILE}"

# Add invalid configuration
ssh ${NODE_NAME} "echo 'invalidKey: true' | sudo tee -a ${CONFIG_FILE}"

# Restart kubelet on node
ssh ${NODE_NAME} "sudo systemctl restart kubelet"

# Wait for node to become NotReady (up to 60 seconds)
echo "Waiting for node ${NODE_NAME} to become NotReady..."
timeout 60 bash -c "until ! kubectl get node ${NODE_NAME} | grep -q Ready; do sleep 5; done"

# Output the practice question
echo -e "\n${GREEN}=== CKA Practice Question ===${NC}"
echo "Troubleshoot why the node '${NODE_NAME}' is in NotReady state."
echo "Identify the issue with the kubelet configuration, fix it, and ensure the node returns to Ready state."
echo -e "\n${GREEN}Setup complete. You can now attempt the practice question.${NC}"