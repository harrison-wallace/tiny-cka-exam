#!/bin/bash

# Verification script for CKA practice question: CronJob Curling Nginx Service Not Working

# Variables
NAMESPACE="default"
CRONJOB_NAME="curl-cron"
SERVICE_NAME="nginx-svc"

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

# Check 1: CronJob exists
echo -n "Checking if CronJob '${CRONJOB_NAME}' exists in namespace '${NAMESPACE}'... "
if kubectl -n ${NAMESPACE} get cronjob ${CRONJOB_NAME} &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED: CronJob '${CRONJOB_NAME}' not found.${NC}"
    STATUS=1
fi

# Check 2: Command uses correct service DNS
echo -n "Checking if command uses correct service DNS... "
COMMAND_ARG=$(kubectl -n ${NAMESPACE} get cronjob ${CRONJOB_NAME} -o jsonpath='{.spec.jobTemplate.spec.template.spec.containers[0].command[1]}')
if [ "$COMMAND_ARG" = "${SERVICE_NAME}.${NAMESPACE}.svc.cluster.local" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED: Command arg is '${COMMAND_ARG}', expected '${SERVICE_NAME}.${NAMESPACE}.svc.cluster.local'.${NC}"
    STATUS=1
fi

# Check 3: Latest job is successful
LATEST_JOB=$(kubectl -n ${NAMESPACE} get jobs --selector=job-name=${CRONJOB_NAME}-* --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')
echo -n "Checking if latest job is successful... "
if kubectl -n ${NAMESPACE} get job ${LATEST_JOB} -o jsonpath='{.status.succeeded}' | grep -q 1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED: Latest job did not succeed.${NC}"
    STATUS=1
fi

# Final result
if [ ${STATUS} -eq 0 ]; then
    echo -e "\n${GREEN}All checks passed! The practice question task was completed correctly.${NC}"
else
    echo -e "\n${RED}Some checks failed. Please review the errors above and try again.${NC}"
fi

exit ${STATUS}