#!/bin/bash

# Verification script for CKA practice question: Sidecar Logging Configuration Error

# Variables
NAMESPACE="sidecar-ns"
POD_NAME="logging-pod"

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

# Check 1: Pod is Running
echo -n "Checking if pod '${POD_NAME}' is Running... "
if kubectl -n ${NAMESPACE} get pod ${POD_NAME} | grep -q Running; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED: Pod '${POD_NAME}' is not Running.${NC}"
    STATUS=1
fi

# Check 2: Sidecar mount path is fixed
echo -n "Checking if sidecar mount path is fixed... "
MOUNT_PATH=$(kubectl -n ${NAMESPACE} get pod ${POD_NAME} -o jsonpath='{.spec.containers[1].volumeMounts[0].mountPath}')
if [ "$MOUNT_PATH" = "/var/log/nginx" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED: Mount path is '${MOUNT_PATH}', expected '/var/log/nginx'.${NC}"
    STATUS=1
fi

# Check 3: Sidecar command uses correct path
echo -n "Checking if sidecar command uses correct path... "
COMMAND=$(kubectl -n ${NAMESPACE} get pod ${POD_NAME} -o jsonpath='{.spec.containers[1].command[2]}')
if echo "$COMMAND" | grep -q "/var/log/nginx/access.log"; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED: Command does not use correct log path.${NC}"
    STATUS=1
fi

# Final result
if [ ${STATUS} -eq 0 ]; then
    echo -e "\n${GREEN}All checks passed! The practice question task was completed correctly.${NC}"
else
    echo -e "\n${RED}Some checks failed. Please review the errors above and try again.${NC}"
fi

exit ${STATUS}