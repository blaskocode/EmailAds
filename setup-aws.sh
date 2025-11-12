#!/bin/bash

#############################################
# HiBid Email MVP - AWS Infrastructure Setup
# Automated script for complete AWS deployment
#############################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="hibid-email-mvp"
AWS_REGION="us-east-1"
INSTANCE_TYPE="t3.medium"
VOLUME_SIZE="30"

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}HiBid Email MVP - AWS Setup${NC}"
echo -e "${GREEN}======================================${NC}\n"

# Function to print status messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    log_error "AWS CLI is not configured. Run 'aws configure' first."
    exit 1
fi

log_info "AWS CLI is configured and ready"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
log_info "AWS Account ID: $AWS_ACCOUNT_ID"

# Create unique S3 bucket name
S3_BUCKET_NAME="${PROJECT_NAME}-assets-$(date +%s)"

echo -e "\n${YELLOW}Configuration:${NC}"
echo "  Project Name: $PROJECT_NAME"
echo "  AWS Region: $AWS_REGION"
echo "  Instance Type: $INSTANCE_TYPE"
echo "  S3 Bucket: $S3_BUCKET_NAME"
echo ""
read -p "Continue with this configuration? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_warn "Setup cancelled by user"
    exit 0
fi

#############################################
# 1. Create S3 Bucket
#############################################
log_info "Creating S3 bucket: $S3_BUCKET_NAME"
if aws s3 mb s3://${S3_BUCKET_NAME} --region ${AWS_REGION} 2>&1; then
    log_info "S3 bucket created successfully"
else
    log_error "Failed to create S3 bucket"
    exit 1
fi

# Enable versioning
log_info "Enabling S3 versioning"
aws s3api put-bucket-versioning \
    --bucket ${S3_BUCKET_NAME} \
    --versioning-configuration Status=Enabled

# Configure CORS
log_info "Configuring S3 CORS"
cat > /tmp/cors-config.json << EOF
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF

aws s3api put-bucket-cors \
    --bucket ${S3_BUCKET_NAME} \
    --cors-configuration file:///tmp/cors-config.json

# Configure lifecycle policy
log_info "Configuring S3 lifecycle policy (30-day retention)"
cat > /tmp/lifecycle-policy.json << EOF
{
  "Rules": [
    {
      "ID": "DeleteOldAssets",
      "Status": "Enabled",
      "Prefix": "",
      "Expiration": {
        "Days": 30
      }
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket ${S3_BUCKET_NAME} \
    --lifecycle-configuration file:///tmp/lifecycle-policy.json

#############################################
# 2. Create IAM Role and Policies
#############################################
log_info "Creating IAM role for EC2"

# Create trust policy
cat > /tmp/trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
if aws iam create-role \
    --role-name ${PROJECT_NAME}-ec2-role \
    --assume-role-policy-document file:///tmp/trust-policy.json \
    --description "Role for HiBid Email MVP EC2 instance" 2>&1; then
    log_info "IAM role created successfully"
else
    log_warn "IAM role might already exist, continuing..."
fi

# Create S3 access policy
log_info "Creating S3 access policy"
cat > /tmp/s3-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::${S3_BUCKET_NAME}/*",
        "arn:aws:s3:::${S3_BUCKET_NAME}"
      ]
    }
  ]
}
EOF

# Create policy
POLICY_ARN=""
if aws iam create-policy \
    --policy-name ${PROJECT_NAME}-s3-policy \
    --policy-document file:///tmp/s3-policy.json \
    --description "S3 access policy for HiBid Email MVP" 2>&1; then
    log_info "IAM policy created successfully"
    POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${PROJECT_NAME}-s3-policy"
else
    log_warn "IAM policy might already exist, retrieving ARN..."
    POLICY_ARN=$(aws iam list-policies --query "Policies[?PolicyName=='${PROJECT_NAME}-s3-policy'].Arn" --output text)
fi

# Attach policy to role
log_info "Attaching policy to role"
aws iam attach-role-policy \
    --role-name ${PROJECT_NAME}-ec2-role \
    --policy-arn ${POLICY_ARN}

# Attach CloudWatch logs policy
log_info "Attaching CloudWatch logs policy"
aws iam attach-role-policy \
    --role-name ${PROJECT_NAME}-ec2-role \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

# Create instance profile
log_info "Creating instance profile"
if aws iam create-instance-profile \
    --instance-profile-name ${PROJECT_NAME}-instance-profile 2>&1; then
    log_info "Instance profile created"
else
    log_warn "Instance profile might already exist"
fi

# Add role to instance profile
aws iam add-role-to-instance-profile \
    --instance-profile-name ${PROJECT_NAME}-instance-profile \
    --role-name ${PROJECT_NAME}-ec2-role 2>/dev/null || log_warn "Role already added to instance profile"

# Wait for instance profile to be ready
log_info "Waiting for instance profile to propagate..."
sleep 10

#############################################
# 3. Create Security Group
#############################################
log_info "Getting default VPC ID"
VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=isDefault,Values=true" \
    --query "Vpcs[0].VpcId" \
    --output text)

if [ "$VPC_ID" == "None" ] || [ -z "$VPC_ID" ]; then
    log_error "No default VPC found. Please create a VPC first."
    exit 1
fi

log_info "Using VPC: $VPC_ID"

log_info "Creating security group"
SG_ID=$(aws ec2 create-security-group \
    --group-name ${PROJECT_NAME}-sg \
    --description "Security group for HiBid Email MVP" \
    --vpc-id ${VPC_ID} \
    --query 'GroupId' \
    --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=${PROJECT_NAME}-sg" \
    --query "SecurityGroups[0].GroupId" \
    --output text)

log_info "Security Group ID: $SG_ID"

# Add ingress rules
log_info "Configuring security group rules"

# SSH (port 22)
aws ec2 authorize-security-group-ingress \
    --group-id ${SG_ID} \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 2>/dev/null || log_warn "SSH rule already exists"

# HTTP (port 80)
aws ec2 authorize-security-group-ingress \
    --group-id ${SG_ID} \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 2>/dev/null || log_warn "HTTP rule already exists"

# HTTPS (port 443)
aws ec2 authorize-security-group-ingress \
    --group-id ${SG_ID} \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 2>/dev/null || log_warn "HTTPS rule already exists"

# Backend API (port 8000)
aws ec2 authorize-security-group-ingress \
    --group-id ${SG_ID} \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 2>/dev/null || log_warn "Backend API rule already exists"

# Frontend (port 3000)
aws ec2 authorize-security-group-ingress \
    --group-id ${SG_ID} \
    --protocol tcp \
    --port 3000 \
    --cidr 0.0.0.0/0 2>/dev/null || log_warn "Frontend rule already exists"

#############################################
# 4. Create SSH Key Pair
#############################################
KEY_NAME="${PROJECT_NAME}-key"
KEY_FILE="${KEY_NAME}.pem"

if [ -f "$KEY_FILE" ]; then
    log_warn "Key file $KEY_FILE already exists. Skipping key creation."
else
    log_info "Creating SSH key pair"
    aws ec2 create-key-pair \
        --key-name ${KEY_NAME} \
        --query 'KeyMaterial' \
        --output text > ${KEY_FILE}
    
    chmod 400 ${KEY_FILE}
    log_info "SSH key saved to: $KEY_FILE"
fi

#############################################
# 5. Create User Data Script
#############################################
log_info "Creating user data script"
cat > /tmp/user-data.sh << 'USERDATA'
#!/bin/bash
set -e

# Log all output
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "Starting user data script..."

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install other tools
apt-get install -y git nginx certbot python3-certbot-nginx htop

# Create application directory
mkdir -p /opt/hibid-email-mvp/data
mkdir -p /opt/hibid-email-mvp/logs
mkdir -p /opt/hibid-email-mvp/backups
chown -R ubuntu:ubuntu /opt/hibid-email-mvp

# Install CloudWatch agent
wget -q https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb
rm amazon-cloudwatch-agent.deb

echo "User data script completed successfully"
USERDATA

#############################################
# 6. Launch EC2 Instance
#############################################
log_info "Getting latest Ubuntu 22.04 AMI"
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text)

log_info "Using AMI: $AMI_ID"

log_info "Launching EC2 instance"
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ${AMI_ID} \
    --instance-type ${INSTANCE_TYPE} \
    --key-name ${KEY_NAME} \
    --security-group-ids ${SG_ID} \
    --iam-instance-profile Name=${PROJECT_NAME}-instance-profile \
    --block-device-mappings "[{\"DeviceName\":\"/dev/sda1\",\"Ebs\":{\"VolumeSize\":${VOLUME_SIZE},\"VolumeType\":\"gp3\",\"DeleteOnTermination\":false}}]" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT_NAME}},{Key=Project,Value=HiBid-Email-MVP}]" \
    --user-data file:///tmp/user-data.sh \
    --query 'Instances[0].InstanceId' \
    --output text)

log_info "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
log_info "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids ${INSTANCE_ID}

# Get public IP
INSTANCE_IP=$(aws ec2 describe-instances \
    --instance-ids ${INSTANCE_ID} \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

log_info "Instance is running at: $INSTANCE_IP"

#############################################
# 7. Allocate Elastic IP
#############################################
log_info "Allocating Elastic IP"
ALLOCATION_ID=$(aws ec2 allocate-address \
    --domain vpc \
    --query 'AllocationId' \
    --output text)

# Associate with instance
aws ec2 associate-address \
    --instance-id ${INSTANCE_ID} \
    --allocation-id ${ALLOCATION_ID}

# Get Elastic IP
ELASTIC_IP=$(aws ec2 describe-addresses \
    --allocation-ids ${ALLOCATION_ID} \
    --query 'Addresses[0].PublicIp' \
    --output text)

log_info "Elastic IP allocated: $ELASTIC_IP"

#############################################
# 8. Create Configuration File
#############################################
log_info "Creating deployment configuration file"
cat > deployment-config.env << EOF
# HiBid Email MVP - Deployment Configuration
# Generated: $(date)

# AWS Resources
AWS_REGION=${AWS_REGION}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}
S3_BUCKET_NAME=${S3_BUCKET_NAME}
VPC_ID=${VPC_ID}
SECURITY_GROUP_ID=${SG_ID}
INSTANCE_ID=${INSTANCE_ID}
ELASTIC_IP=${ELASTIC_IP}
KEY_FILE=${KEY_FILE}

# SSH Access
SSH_COMMAND="ssh -i ${KEY_FILE} ubuntu@${ELASTIC_IP}"

# Application URLs
FRONTEND_URL=http://${ELASTIC_IP}:3000
BACKEND_URL=http://${ELASTIC_IP}:8000
EOF

#############################################
# 9. Wait for Instance Initialization
#############################################
log_info "Waiting for instance to complete initialization (this may take 5-10 minutes)..."
log_info "You can monitor progress with: tail -f /var/log/user-data.log"

# Wait 2 minutes for user data script to complete
sleep 120

# Check if user data completed
log_info "Checking instance status..."
for i in {1..10}; do
    if ssh -i ${KEY_FILE} -o StrictHostKeyChecking=no ubuntu@${ELASTIC_IP} "grep -q 'User data script completed' /var/log/user-data.log" 2>/dev/null; then
        log_info "Instance initialization completed successfully"
        break
    fi
    log_warn "Instance still initializing... (attempt $i/10)"
    sleep 30
done

#############################################
# 10. Summary
#############################################
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${YELLOW}AWS Resources Created:${NC}"
echo "  S3 Bucket: $S3_BUCKET_NAME"
echo "  IAM Role: ${PROJECT_NAME}-ec2-role"
echo "  Security Group: $SG_ID"
echo "  EC2 Instance: $INSTANCE_ID"
echo "  Elastic IP: $ELASTIC_IP"
echo ""
echo -e "${YELLOW}Access Information:${NC}"
echo "  SSH: ssh -i ${KEY_FILE} ubuntu@${ELASTIC_IP}"
echo "  Frontend: http://${ELASTIC_IP}:3000"
echo "  Backend: http://${ELASTIC_IP}:8000"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. SSH to instance: ssh -i ${KEY_FILE} ubuntu@${ELASTIC_IP}"
echo "  2. Upload your application code"
echo "  3. Create .env file with OPENAI_API_KEY and other secrets"
echo "  4. Run: cd /opt/hibid-email-mvp && docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo -e "${YELLOW}Configuration saved to:${NC} deployment-config.env"
echo ""

# Save summary to file
cat > deployment-summary.txt << EOF
HiBid Email MVP - Deployment Summary
Generated: $(date)

AWS Resources:
- S3 Bucket: $S3_BUCKET_NAME
- IAM Role: ${PROJECT_NAME}-ec2-role
- Security Group: $SG_ID
- EC2 Instance: $INSTANCE_ID
- Elastic IP: $ELASTIC_IP

Access Information:
- SSH: ssh -i ${KEY_FILE} ubuntu@${ELASTIC_IP}
- Frontend URL: http://${ELASTIC_IP}:3000
- Backend URL: http://${ELASTIC_IP}:8000
- Backend API: http://${ELASTIC_IP}:8000/api/v1

SSH Key File: ${KEY_FILE}
Configuration File: deployment-config.env

Next Steps:
1. SSH to instance
2. Upload application code
3. Configure environment variables
4. Deploy application with Docker Compose
EOF

log_info "Summary saved to: deployment-summary.txt"
echo ""
log_info "Setup script completed successfully!"
