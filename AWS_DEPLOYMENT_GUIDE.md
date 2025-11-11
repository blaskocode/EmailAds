# HiBid Email MVP - AWS Deployment Guide

**Version:** 1.0  
**Target Environment:** AWS (EC2 + S3 + EBS)  
**Deployment Method:** Docker Containers  
**Estimated Setup Time:** 2-3 hours

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Infrastructure Setup](#aws-infrastructure-setup)
3. [S3 Bucket Configuration](#s3-bucket-configuration)
4. [IAM Roles & Policies](#iam-roles--policies)
5. [EC2 Instance Setup](#ec2-instance-setup)
6. [Application Deployment](#application-deployment)
7. [SSL Certificate Setup](#ssl-certificate-setup)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Disaster Recovery](#backup--disaster-recovery)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version

# Install Docker (on local machine for testing)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### AWS Account Setup
- [ ] AWS account with admin access
- [ ] AWS CLI configured with credentials
- [ ] OpenAI API key ready
- [ ] Domain name (optional, can use EC2 public IP)

### Configure AWS CLI
```bash
aws configure
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]
# Default region name: us-east-1
# Default output format: json
```

---

## AWS Infrastructure Setup

### Architecture Overview
```
Internet
   ↓
[Route 53] (Optional DNS)
   ↓
[Application Load Balancer] (Optional)
   ↓
[EC2 Instance - t3.medium]
   ├─→ Docker: Frontend (port 3000)
   ├─→ Docker: Backend (port 8000)
   ├─→ SQLite on EBS Volume
   └─→ Logs on EBS Volume
   ↓
[S3 Bucket] - Asset Storage
```

### Step 1: Choose AWS Region
```bash
# Set your preferred region
export AWS_REGION=us-east-1
export PROJECT_NAME=hibid-email-mvp
```

### Step 2: Create VPC (if not using default)
```bash
# For MVP, we'll use the default VPC
# Get default VPC ID
aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text

# Store VPC ID
export VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)
echo "VPC ID: $VPC_ID"
```

---

## S3 Bucket Configuration

### Step 1: Create S3 Bucket
```bash
# Create bucket with unique name
export S3_BUCKET_NAME="${PROJECT_NAME}-assets-$(date +%s)"

aws s3 mb s3://${S3_BUCKET_NAME} --region ${AWS_REGION}

echo "S3 Bucket created: ${S3_BUCKET_NAME}"
```

### Step 2: Configure Bucket Policy
Create file: `s3-bucket-policy.json`
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowApplicationAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:role/hibid-email-ec2-role"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::BUCKET_NAME/*",
        "arn:aws:s3:::BUCKET_NAME"
      ]
    }
  ]
}
```

### Step 3: Enable CORS for S3
Create file: `s3-cors-config.json`
```json
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
```

Apply CORS configuration:
```bash
aws s3api put-bucket-cors \
  --bucket ${S3_BUCKET_NAME} \
  --cors-configuration file://s3-cors-config.json
```

### Step 4: Enable Versioning (Optional but Recommended)
```bash
aws s3api put-bucket-versioning \
  --bucket ${S3_BUCKET_NAME} \
  --versioning-configuration Status=Enabled
```

### Step 5: Set Lifecycle Policy (Auto-delete old files after 30 days)
Create file: `s3-lifecycle-policy.json`
```json
{
  "Rules": [
    {
      "Id": "DeleteOldAssets",
      "Status": "Enabled",
      "Prefix": "",
      "Expiration": {
        "Days": 30
      }
    }
  ]
}
```

Apply lifecycle policy:
```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket ${S3_BUCKET_NAME} \
  --lifecycle-configuration file://s3-lifecycle-policy.json
```

---

## IAM Roles & Policies

### Step 1: Create IAM Role for EC2
Create file: `ec2-trust-policy.json`
```json
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
```

Create the role:
```bash
aws iam create-role \
  --role-name hibid-email-ec2-role \
  --assume-role-policy-document file://ec2-trust-policy.json
```

### Step 2: Create IAM Policy for S3 Access
Create file: `s3-access-policy.json`
```json
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
        "arn:aws:s3:::BUCKET_NAME/*",
        "arn:aws:s3:::BUCKET_NAME"
      ]
    }
  ]
}
```

Replace BUCKET_NAME and create policy:
```bash
# Replace BUCKET_NAME in the policy file
sed -i "s/BUCKET_NAME/${S3_BUCKET_NAME}/g" s3-access-policy.json

# Create the policy
aws iam create-policy \
  --policy-name hibid-email-s3-policy \
  --policy-document file://s3-access-policy.json

# Get policy ARN
export POLICY_ARN=$(aws iam list-policies --query "Policies[?PolicyName=='hibid-email-s3-policy'].Arn" --output text)
```

### Step 3: Attach Policy to Role
```bash
aws iam attach-role-policy \
  --role-name hibid-email-ec2-role \
  --policy-arn ${POLICY_ARN}
```

### Step 4: Create Instance Profile
```bash
aws iam create-instance-profile \
  --instance-profile-name hibid-email-instance-profile

aws iam add-role-to-instance-profile \
  --instance-profile-name hibid-email-instance-profile \
  --role-name hibid-email-ec2-role
```

---

## EC2 Instance Setup

### Step 1: Create Security Group
```bash
# Create security group
aws ec2 create-security-group \
  --group-name hibid-email-sg \
  --description "Security group for HiBid Email MVP" \
  --vpc-id ${VPC_ID}

# Get security group ID
export SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=hibid-email-sg" --query "SecurityGroups[0].GroupId" --output text)

echo "Security Group ID: ${SG_ID}"
```

### Step 2: Configure Security Group Rules
```bash
# Allow SSH (port 22) - Replace with your IP for security
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Allow HTTP (port 80)
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS (port 443)
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow Backend API (port 8000) - for testing, restrict in production
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0

# Allow Frontend (port 3000) - for testing, restrict in production
aws ec2 authorize-security-group-ingress \
  --group-id ${SG_ID} \
  --protocol tcp \
  --port 3000 \
  --cidr 0.0.0.0/0
```

### Step 3: Create or Import SSH Key Pair
```bash
# Option 1: Create new key pair
aws ec2 create-key-pair \
  --key-name hibid-email-key \
  --query 'KeyMaterial' \
  --output text > hibid-email-key.pem

chmod 400 hibid-email-key.pem

# Option 2: Import existing public key
# aws ec2 import-key-pair --key-name hibid-email-key --public-key-material fileb://~/.ssh/id_rsa.pub
```

### Step 4: Launch EC2 Instance
```bash
# Get latest Ubuntu 22.04 AMI
export AMI_ID=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text)

echo "Using AMI: ${AMI_ID}"

# Launch instance
aws ec2 run-instances \
  --image-id ${AMI_ID} \
  --instance-type t3.medium \
  --key-name hibid-email-key \
  --security-group-ids ${SG_ID} \
  --iam-instance-profile Name=hibid-email-instance-profile \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":30,"VolumeType":"gp3"}}]' \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT_NAME}}]" \
  --user-data file://user-data.sh

# Get instance ID
export INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=${PROJECT_NAME}" "Name=instance-state-name,Values=running,pending" \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text)

echo "Instance ID: ${INSTANCE_ID}"
```

### Step 5: Create User Data Script
Create file: `user-data.sh`
```bash
#!/bin/bash
set -e

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

# Install Git
apt-get install -y git

# Create application directory
mkdir -p /opt/hibid-email-mvp
chown ubuntu:ubuntu /opt/hibid-email-mvp

# Create data directory for SQLite
mkdir -p /opt/hibid-email-mvp/data
chown ubuntu:ubuntu /opt/hibid-email-mvp/data

# Install CloudWatch agent (optional, for monitoring)
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb

echo "User data script completed" > /var/log/user-data-complete.log
```

### Step 6: Wait for Instance to be Ready
```bash
aws ec2 wait instance-running --instance-ids ${INSTANCE_ID}

# Get public IP
export INSTANCE_IP=$(aws ec2 describe-instances \
  --instance-ids ${INSTANCE_ID} \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Instance is running at: ${INSTANCE_IP}"
echo "SSH command: ssh -i hibid-email-key.pem ubuntu@${INSTANCE_IP}"
```

### Step 7: Allocate Elastic IP (Optional but Recommended)
```bash
# Allocate Elastic IP
aws ec2 allocate-address --domain vpc

# Get allocation ID
export ALLOCATION_ID=$(aws ec2 describe-addresses --filters "Name=domain,Values=vpc" --query 'Addresses[0].AllocationId' --output text)

# Associate with instance
aws ec2 associate-address \
  --instance-id ${INSTANCE_ID} \
  --allocation-id ${ALLOCATION_ID}

# Get new Elastic IP
export ELASTIC_IP=$(aws ec2 describe-addresses --allocation-ids ${ALLOCATION_ID} --query 'Addresses[0].PublicIp' --output text)

echo "Elastic IP: ${ELASTIC_IP}"
echo "Update your DNS to point to: ${ELASTIC_IP}"
```

---

## Application Deployment

### Step 1: Connect to EC2 Instance
```bash
ssh -i hibid-email-key.pem ubuntu@${INSTANCE_IP}
```

### Step 2: Clone Repository (or Upload Files)
```bash
# On EC2 instance
cd /opt/hibid-email-mvp

# Option 1: Clone from Git (if you have a repo)
# git clone https://github.com/your-org/hibid-email-mvp.git .

# Option 2: Upload files via SCP (from local machine)
# scp -i hibid-email-key.pem -r ./hibid-email-mvp/* ubuntu@${INSTANCE_IP}:/opt/hibid-email-mvp/
```

### Step 3: Create Production Environment File
Create file: `/opt/hibid-email-mvp/.env`
```bash
# Backend Configuration
OPENAI_API_KEY=sk-your-openai-key-here
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name

# Database
DATABASE_URL=sqlite:////opt/hibid-email-mvp/data/campaigns.db

# Application Settings
ENVIRONMENT=production
FRONTEND_URL=http://YOUR_DOMAIN_OR_IP:3000
BACKEND_URL=http://YOUR_DOMAIN_OR_IP:8000

# API Configuration
API_RATE_LIMIT=100
MAX_UPLOAD_SIZE=5242880

# Security
ALLOWED_ORIGINS=http://YOUR_DOMAIN_OR_IP:3000,https://YOUR_DOMAIN

# Logging
LOG_LEVEL=INFO
```

**Important:** Replace all placeholder values with actual credentials.

### Step 4: Create Production Docker Compose File
Create file: `/opt/hibid-email-mvp/docker-compose.prod.yml`
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: hibid-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - /opt/hibid-email-mvp/data:/app/data
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build: 
      context: ./frontend
      args:
        - VITE_API_URL=http://${INSTANCE_IP}:8000
    container_name: hibid-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    depends_on:
      backend:
        condition: service_healthy
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  data:
    driver: local
```

### Step 5: Build and Deploy
```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 6: Verify Deployment
```bash
# Test backend health
curl http://localhost:8000/health

# Test frontend (from your local machine)
curl http://${INSTANCE_IP}:3000

# Check if services are running
docker ps
```

---

## SSL Certificate Setup

### Option 1: Let's Encrypt with Nginx (Recommended)

#### Step 1: Install Nginx
```bash
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

#### Step 2: Configure Nginx as Reverse Proxy
Create file: `/etc/nginx/sites-available/hibid-email`
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL certificates (will be added by certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # File upload settings
        client_max_body_size 10M;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

#### Step 3: Enable Site and Obtain Certificate
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/hibid-email /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### Option 2: AWS Certificate Manager (ALB)

If using Application Load Balancer:

```bash
# Request certificate
aws acm request-certificate \
  --domain-name your-domain.com \
  --subject-alternative-names www.your-domain.com \
  --validation-method DNS

# Follow the DNS validation steps in AWS Console
```

---

## Monitoring & Logging

### Step 1: Set Up CloudWatch Logs

Create file: `/opt/aws/amazon-cloudwatch-agent/etc/config.json`
```json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/opt/hibid-email-mvp/logs/backend.log",
            "log_group_name": "/hibid-email/backend",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "/hibid-email/nginx-access",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "/hibid-email/nginx-error",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "HiBidEmail",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {"name": "cpu_usage_idle", "rename": "CPU_IDLE", "unit": "Percent"},
          "cpu_usage_iowait"
        ],
        "totalcpu": false
      },
      "disk": {
        "measurement": [
          {"name": "used_percent", "rename": "DISK_USED", "unit": "Percent"}
        ],
        "resources": ["/"]
      },
      "mem": {
        "measurement": [
          {"name": "mem_used_percent", "rename": "MEM_USED", "unit": "Percent"}
        ]
      }
    }
  }
}
```

Start CloudWatch agent:
```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### Step 2: Set Up CloudWatch Alarms
```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name hibid-email-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=${INSTANCE_ID} \
  --evaluation-periods 2

# Disk space alarm
aws cloudwatch put-metric-alarm \
  --alarm-name hibid-email-disk-full \
  --alarm-description "Alert when disk usage exceeds 85%" \
  --metric-name DISK_USED \
  --namespace HiBidEmail \
  --statistic Average \
  --period 300 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

### Step 3: Application Logging

Add to backend code (`backend/app/main.py`):
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# File handler
file_handler = RotatingFileHandler(
    '/app/logs/backend.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
file_handler.setFormatter(log_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
```

### Step 4: Simple Uptime Monitoring Script

Create file: `/opt/hibid-email-mvp/monitor.sh`
```bash
#!/bin/bash

CHECK_INTERVAL=60  # seconds
LOG_FILE="/opt/hibid-email-mvp/logs/uptime-monitor.log"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check backend
    BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    
    # Check frontend
    FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
    
    if [ "$BACKEND_STATUS" != "200" ]; then
        echo "$TIMESTAMP - ERROR: Backend health check failed (Status: $BACKEND_STATUS)" >> $LOG_FILE
        # Restart backend if needed
        docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml restart backend
    fi
    
    if [ "$FRONTEND_STATUS" != "200" ]; then
        echo "$TIMESTAMP - ERROR: Frontend health check failed (Status: $FRONTEND_STATUS)" >> $LOG_FILE
        # Restart frontend if needed
        docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml restart frontend
    fi
    
    sleep $CHECK_INTERVAL
done
```

Make executable and run:
```bash
chmod +x /opt/hibid-email-mvp/monitor.sh
nohup /opt/hibid-email-mvp/monitor.sh &
```

---

## Backup & Disaster Recovery

### Step 1: Automated Database Backup Script

Create file: `/opt/hibid-email-mvp/backup.sh`
```bash
#!/bin/bash

BACKUP_DIR="/opt/hibid-email-mvp/backups"
DB_FILE="/opt/hibid-email-mvp/data/campaigns.db"
S3_BACKUP_BUCKET="hibid-email-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup database
sqlite3 $DB_FILE ".backup '$BACKUP_DIR/campaigns_$TIMESTAMP.db'"

# Compress backup
gzip $BACKUP_DIR/campaigns_$TIMESTAMP.db

# Upload to S3
aws s3 cp $BACKUP_DIR/campaigns_$TIMESTAMP.db.gz s3://$S3_BACKUP_BUCKET/database/

# Keep only last 7 days of local backups
find $BACKUP_DIR -name "campaigns_*.db.gz" -mtime +7 -delete

echo "Backup completed: campaigns_$TIMESTAMP.db.gz"
```

### Step 2: Set Up Cron Job for Automated Backups
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/hibid-email-mvp/backup.sh >> /opt/hibid-email-mvp/logs/backup.log 2>&1
```

### Step 3: EBS Snapshot Policy
```bash
# Create snapshot of EBS volume
aws ec2 create-snapshot \
  --volume-id $(aws ec2 describe-volumes --filters "Name=attachment.instance-id,Values=${INSTANCE_ID}" --query "Volumes[0].VolumeId" --output text) \
  --description "HiBid Email MVP - $(date +%Y-%m-%d)"

# Create automated snapshot lifecycle policy via AWS Console
# or use AWS Backup service
```

### Step 4: Disaster Recovery Plan

**Recovery Steps:**
1. Launch new EC2 instance with same configuration
2. Attach EBS snapshot or restore from S3 backup
3. Deploy application using same docker-compose configuration
4. Update DNS/Elastic IP to point to new instance
5. Verify all services are running

**RTO (Recovery Time Objective):** 30 minutes  
**RPO (Recovery Point Objective):** 24 hours (daily backups)

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Docker Containers Won't Start
```bash
# Check Docker logs
docker-compose -f docker-compose.prod.yml logs

# Check if ports are already in use
sudo netstat -tulpn | grep -E '3000|8000'

# Restart Docker service
sudo systemctl restart docker
```

#### 2. S3 Access Denied Errors
```bash
# Verify IAM role is attached
aws ec2 describe-instances --instance-ids ${INSTANCE_ID} --query 'Reservations[0].Instances[0].IamInstanceProfile'

# Test S3 access from EC2
aws s3 ls s3://${S3_BUCKET_NAME}/

# Check bucket policy
aws s3api get-bucket-policy --bucket ${S3_BUCKET_NAME}
```

#### 3. High Memory Usage
```bash
# Check memory usage
free -h

# Check Docker container memory
docker stats

# Restart containers to clear memory
docker-compose -f docker-compose.prod.yml restart
```

#### 4. Slow Performance
```bash
# Check system resources
htop

# Check disk I/O
iostat -x 1

# Check database size
du -sh /opt/hibid-email-mvp/data/campaigns.db

# Optimize SQLite database
sqlite3 /opt/hibid-email-mvp/data/campaigns.db "VACUUM;"
```

#### 5. OpenAI API Timeout
```bash
# Check network connectivity
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"

# Increase timeout in backend config
# Edit backend/app/config.py:
# OPENAI_TIMEOUT = 30  # seconds
```

### Debug Mode

Enable detailed logging:
```bash
# Stop containers
docker-compose -f docker-compose.prod.yml down

# Edit .env file
echo "LOG_LEVEL=DEBUG" >> .env

# Restart with verbose logging
docker-compose -f docker-compose.prod.yml up
```

### Health Check Commands
```bash
# Full system health check
echo "=== Backend Health ==="
curl http://localhost:8000/health

echo -e "\n=== Frontend Health ==="
curl -I http://localhost:3000

echo -e "\n=== Docker Status ==="
docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml ps

echo -e "\n=== Disk Usage ==="
df -h

echo -e "\n=== Memory Usage ==="
free -h

echo -e "\n=== Database Size ==="
du -sh /opt/hibid-email-mvp/data/campaigns.db
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] AWS CLI configured
- [ ] OpenAI API key obtained
- [ ] Domain name configured (optional)
- [ ] S3 bucket created
- [ ] IAM roles and policies configured
- [ ] Security group configured
- [ ] SSH key pair created

### Deployment
- [ ] EC2 instance launched
- [ ] Docker and Docker Compose installed
- [ ] Application code deployed
- [ ] Environment variables configured
- [ ] Docker containers built and running
- [ ] Health checks passing
- [ ] SSL certificate configured (if using HTTPS)

### Post-Deployment
- [ ] DNS configured to point to instance
- [ ] Backup script configured and tested
- [ ] Monitoring enabled
- [ ] CloudWatch alarms set up
- [ ] Documentation updated
- [ ] Team notified of deployment

### Testing
- [ ] Upload test campaign
- [ ] AI processing works (<5 seconds)
- [ ] Preview renders correctly
- [ ] Approval workflow functions
- [ ] Download HTML works
- [ ] Load testing completed
- [ ] Security scan performed

---

## Maintenance Tasks

### Daily
- [ ] Check application logs for errors
- [ ] Verify backups completed successfully
- [ ] Monitor CloudWatch metrics

### Weekly
- [ ] Review disk space usage
- [ ] Check for security updates
- [ ] Review access logs

### Monthly
- [ ] Update dependencies
- [ ] Test disaster recovery procedure
- [ ] Review and optimize costs
- [ ] Clean up old S3 assets (>30 days)

---

## Cost Estimation

### Monthly AWS Costs (Approximate)

| Service | Specification | Monthly Cost |
|---------|--------------|--------------|
| EC2 t3.medium | 2 vCPU, 4GB RAM | ~$30 |
| EBS gp3 Volume | 30GB | ~$2.50 |
| S3 Storage | 50GB (average) | ~$1.15 |
| S3 Requests | 10k PUT, 50k GET | ~$0.10 |
| Data Transfer | 100GB out | ~$9 |
| Elastic IP | 1 IP | Free (if attached) |
| CloudWatch | Basic monitoring | ~$3 |
| **Total** | | **~$45-50/month** |

**Note:** OpenAI API costs are separate and depend on usage.

### Cost Optimization Tips
- Use Reserved Instances for 30-40% savings
- Enable S3 Intelligent-Tiering
- Set up lifecycle policies for old data
- Use CloudFront CDN for static assets
- Monitor and optimize API calls

---

## Security Best Practices

### Application Security
- [ ] Keep secrets in environment variables, never in code
- [ ] Use IAM roles instead of access keys where possible
- [ ] Enable MFA on AWS account
- [ ] Regularly rotate credentials
- [ ] Keep Docker images updated

### Network Security
- [ ] Restrict SSH access to specific IP ranges
- [ ] Use VPC for network isolation (production)
- [ ] Enable VPC Flow Logs
- [ ] Configure WAF rules (if using ALB)
- [ ] Regular security audits

### Data Security
- [ ] Enable S3 bucket encryption
- [ ] Enable EBS volume encryption
- [ ] Regular backups with encryption
- [ ] Secure file upload validation
- [ ] Input sanitization

---

## Quick Command Reference

```bash
# SSH to instance
ssh -i hibid-email-key.pem ubuntu@${INSTANCE_IP}

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update application
cd /opt/hibid-email-mvp
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Backup database
sqlite3 /opt/hibid-email-mvp/data/campaigns.db ".backup '/tmp/backup.db'"

# Check disk space
df -h

# Monitor resources
htop
docker stats
```

---

## Support and Resources

### AWS Documentation
- EC2: https://docs.aws.amazon.com/ec2/
- S3: https://docs.aws.amazon.com/s3/
- IAM: https://docs.aws.amazon.com/iam/
- CloudWatch: https://docs.aws.amazon.com/cloudwatch/

### Docker Documentation
- Docker: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/

### Application Documentation
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/

---

**Document Version:** 1.0  
**Last Updated:** November 11, 2025  
**Maintained By:** DevOps Team

**For urgent issues, contact:** devops@hibid.com
