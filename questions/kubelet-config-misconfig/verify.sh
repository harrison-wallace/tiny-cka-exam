#!/bin/bash

# Verification script for CKA practice question: Kubelet Configuration Misconfiguration

# Variables
NODE_NAME="node01"
CONFIG_FILE="/var/lib/kubelet/config.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Initialize status
STATUS=0

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed.${NC}"
    exit 1
fi

echo "Verifying practice question setup..."

# Check 1: Node is Ready
echo -n "Checking if node '${NODE_NAME}' is Ready... "
if kubectl get node ${NODE_NAME} | grep -q Ready; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED: Node '${NODE_NAME}' is not Ready.${NC}"
    STATUS=1
fi

# Check 2: Config does not contain invalid key
echo -n "Checking if kubelet config on '${NODE_NAME}' is fixed... "
if ssh ${NODE_NAME} "sudo grep -q 'invalidKey:' ${CONFIG_FILE}"; then
    echo -e "${RED}FAILED: Invalid key still present in config.${NC}"
    STATUS=1
else
    echo -e "${GREEN}OK${NC}"
fi

# Final result
if [ ${STATUS} -eq 0 ]; then
    echo -e "\n${GREEN}All checks passed! The practice question task was completed correctly.${NC}"
else
    echo -e "\n${RED}Some checks failed. Please review the errors above and try again.${NC}"
fi

exit ${STATUS}