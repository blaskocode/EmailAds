#!/bin/bash

##################################################
# HiBid Email MVP - AWS Resource Cleanup Script
# WARNING: This will delete ALL resources created
##################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo -e "${RED}======================================${NC}"
echo -e "${RED}HiBid Email MVP - Resource Cleanup${NC}"
echo -e "${RED}======================================${NC}\n"

# Load configuration if available
if [ -f "deployment-config.env" ]; then
    log_info "Loading deployment configuration..."
    source deployment-config.env
else
    log_warn "deployment-config.env not found"
    log_warn "You'll need to provide resource IDs manually"
    
    read -p "Enter Project Name (default: hibid-email-mvp): " PROJECT_NAME
    PROJECT_NAME=${PROJECT_NAME:-hibid-email-mvp}
    
    read -p "Enter AWS Region (default: us-east-1): " AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}
fi

echo ""
echo -e "${RED}WARNING: This will DELETE the following resources:${NC}"
echo "  - EC2 Instance: ${INSTANCE_ID:-Unknown}"
echo "  - Elastic IP: ${ELASTIC_IP:-Unknown}"
echo "  - S3 Bucket: ${S3_BUCKET_NAME:-Unknown}"
echo "  - Security Group: ${SECURITY_GROUP_ID:-Unknown}"
echo "  - IAM Role and Policies"
echo "  - SSH Key Pair"
echo ""
echo -e "${RED}This action CANNOT be undone!${NC}"
echo ""
read -p "Are you absolutely sure? Type 'DELETE' to confirm: " CONFIRM

if [ "$CONFIRM" != "DELETE" ]; then
    log_info "Cleanup cancelled"
    exit 0
fi

echo ""
log_warn "Starting cleanup in 5 seconds... (Ctrl+C to cancel)"
sleep 5

#############################################
# 1. Terminate EC2 Instance
#############################################
if [ ! -z "$INSTANCE_ID" ]; then
    log_info "Terminating EC2 instance: $INSTANCE_ID"
    
    # Disassociate Elastic IP first
    if [ ! -z "$ELASTIC_IP" ]; then
        ASSOCIATION_ID=$(aws ec2 describe-addresses \
            --public-ips ${ELASTIC_IP} \
            --query 'Addresses[0].AssociationId' \
            --output text 2>/dev/null)
        
        if [ "$ASSOCIATION_ID" != "None" ] && [ ! -z "$ASSOCIATION_ID" ]; then
            log_info "Disassociating Elastic IP..."
            aws ec2 disassociate-address --association-id ${ASSOCIATION_ID}
        fi
    fi
    
    # Terminate instance
    aws ec2 terminate-instances --instance-ids ${INSTANCE_ID}
    log_info "Waiting for instance termination..."
    aws ec2 wait instance-terminated --instance-ids ${INSTANCE_ID}
    log_info "Instance terminated"
else
    log_warn "No instance ID found, skipping..."
fi

#############################################
# 2. Release Elastic IP
#############################################
if [ ! -z "$ELASTIC_IP" ]; then
    log_info "Releasing Elastic IP: $ELASTIC_IP"
    
    ALLOCATION_ID=$(aws ec2 describe-addresses \
        --public-ips ${ELASTIC_IP} \
        --query 'Addresses[0].AllocationId' \
        --output text 2>/dev/null)
    
    if [ "$ALLOCATION_ID" != "None" ] && [ ! -z "$ALLOCATION_ID" ]; then
        aws ec2 release-address --allocation-id ${ALLOCATION_ID}
        log_info "Elastic IP released"
    fi
else
    log_warn "No Elastic IP found, skipping..."
fi

#############################################
# 3. Delete S3 Bucket
#############################################
if [ ! -z "$S3_BUCKET_NAME" ]; then
    log_info "Deleting S3 bucket: $S3_BUCKET_NAME"
    
    # Empty bucket first
    log_info "Emptying S3 bucket..."
    aws s3 rm s3://${S3_BUCKET_NAME} --recursive 2>/dev/null || log_warn "Bucket might be empty or already deleted"
    
    # Delete bucket
    aws s3 rb s3://${S3_BUCKET_NAME} --force 2>/dev/null || log_warn "Could not delete bucket"
    log_info "S3 bucket deleted"
else
    log_warn "No S3 bucket name found, skipping..."
fi

#############################################
# 4. Delete Security Group
#############################################
if [ ! -z "$SECURITY_GROUP_ID" ]; then
    log_info "Deleting security group: $SECURITY_GROUP_ID"
    
    # Wait a bit for instance termination to complete
    sleep 10
    
    aws ec2 delete-security-group --group-id ${SECURITY_GROUP_ID} 2>/dev/null || \
        log_warn "Could not delete security group (might still be in use)"
else
    # Try to find by name
    SG_ID=$(aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=${PROJECT_NAME:-hibid-email-mvp}-sg" \
        --query "SecurityGroups[0].GroupId" \
        --output text 2>/dev/null)
    
    if [ "$SG_ID" != "None" ] && [ ! -z "$SG_ID" ]; then
        log_info "Found security group: $SG_ID"
        sleep 10
        aws ec2 delete-security-group --group-id ${SG_ID} 2>/dev/null || \
            log_warn "Could not delete security group"
    fi
fi

#############################################
# 5. Delete IAM Resources
#############################################
PROJECT_NAME=${PROJECT_NAME:-hibid-email-mvp}

log_info "Deleting IAM resources..."

# Detach policies from role
log_info "Detaching IAM policies..."

# Get S3 policy ARN
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
S3_POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${PROJECT_NAME}-s3-policy"

aws iam detach-role-policy \
    --role-name ${PROJECT_NAME}-ec2-role \
    --policy-arn ${S3_POLICY_ARN} 2>/dev/null || log_warn "S3 policy already detached"

aws iam detach-role-policy \
    --role-name ${PROJECT_NAME}-ec2-role \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy 2>/dev/null || log_warn "CloudWatch policy already detached"

# Remove role from instance profile
log_info "Removing role from instance profile..."
aws iam remove-role-from-instance-profile \
    --instance-profile-name ${PROJECT_NAME}-instance-profile \
    --role-name ${PROJECT_NAME}-ec2-role 2>/dev/null || log_warn "Role already removed"

# Delete instance profile
log_info "Deleting instance profile..."
aws iam delete-instance-profile \
    --instance-profile-name ${PROJECT_NAME}-instance-profile 2>/dev/null || log_warn "Instance profile already deleted"

# Delete IAM role
log_info "Deleting IAM role..."
aws iam delete-role \
    --role-name ${PROJECT_NAME}-ec2-role 2>/dev/null || log_warn "IAM role already deleted"

# Delete S3 policy
log_info "Deleting S3 policy..."
aws iam delete-policy \
    --policy-arn ${S3_POLICY_ARN} 2>/dev/null || log_warn "S3 policy already deleted"

#############################################
# 6. Delete SSH Key Pair
#############################################
KEY_NAME="${PROJECT_NAME}-key"
KEY_FILE="${KEY_NAME}.pem"

if [ -f "$KEY_FILE" ]; then
    log_info "Deleting local SSH key file: $KEY_FILE"
    rm -f ${KEY_FILE}
fi

log_info "Deleting SSH key pair from AWS..."
aws ec2 delete-key-pair --key-name ${KEY_NAME} 2>/dev/null || log_warn "Key pair already deleted"

#############################################
# 7. Clean Up Local Files
#############################################
log_info "Cleaning up local configuration files..."

rm -f deployment-config.env
rm -f deployment-summary.txt
rm -f /tmp/trust-policy.json
rm -f /tmp/s3-policy.json
rm -f /tmp/cors-config.json
rm -f /tmp/lifecycle-policy.json
rm -f /tmp/user-data.sh

#############################################
# Summary
#############################################
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
log_info "All AWS resources have been deleted"
log_info "Local configuration files have been cleaned up"
echo ""
log_warn "Note: Some resources may take a few minutes to fully delete"
log_warn "CloudWatch logs and metrics may persist for up to 15 months"
echo ""
