# Get Your App Running - Step by Step Guide

## Current Situation

Your EC2 instance is running but has network connectivity issues preventing SSH and HTTP access. Here's how to fix it:

## Solution: Use AWS Console EC2 Instance Connect

This is the **easiest and fastest** way to access your instance without SSH:

### Step 1: Access via AWS Console

1. **Open AWS Console**: https://console.aws.amazon.com/ec2/
2. **Go to EC2 → Instances**
3. **Find your instance**: `i-0d2ed3a68d73cc750` (or search for "hibid-email-mvp")
4. **Select the instance**
5. **Click "Connect" button** (top right)
6. **Choose "EC2 Instance Connect" tab**
7. **Click "Connect"** - This opens a browser-based terminal!

### Step 2: Once Connected, Check Current Status

```bash
# Check if Docker is running
docker ps

# Check if app directory exists
ls -la /opt/hibid-email-mvp/

# Check if containers are running
docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml ps
```

### Step 3: Deploy/Update the Application

If the app directory doesn't exist or needs updating:

**Option A: Upload via SCP (from your local machine)**

Open a new terminal on your local machine and run:

```bash
cd /Users/courtneyblaskovich/Documents/Projects/EmailAds

# Upload backend and frontend
scp -i hibid-email-mvp-key.pem -r ./backend ubuntu@44.212.209.159:/tmp/
scp -i hibid-email-mvp-key.pem -r ./frontend ubuntu@44.212.209.159:/tmp/
```

**Option B: Use Git (if you have a repo)**

In the EC2 Instance Connect terminal:

```bash
cd /opt
sudo mkdir -p hibid-email-mvp
sudo chown ubuntu:ubuntu hibid-email-mvp
cd hibid-email-mvp
git clone YOUR_REPO_URL .
```

### Step 4: Set Up Environment Variables

In EC2 Instance Connect terminal:

```bash
cd /opt/hibid-email-mvp

# Create .env file
nano .env
```

Add these variables (replace with your actual values):

```bash
# Backend Configuration
OPENAI_API_KEY=sk-your-openai-key-here
AWS_REGION=us-east-1
S3_BUCKET_NAME=hibid-email-mvp-assets-1762970982

# Database
DATABASE_URL=sqlite:////opt/hibid-email-mvp/data/campaigns.db

# Application Settings
ENVIRONMENT=production
FRONTEND_URL=http://44.212.209.159:3000
BACKEND_URL=http://44.212.209.159:8000

# API Configuration
API_RATE_LIMIT=100
MAX_UPLOAD_SIZE=5242880

# Logging
LOG_LEVEL=INFO
```

Save and exit (Ctrl+X, then Y, then Enter)

### Step 5: Create Docker Compose File

```bash
cd /opt/hibid-email-mvp

cat > docker-compose.prod.yml << 'EOF'
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
      - /opt/hibid-email-mvp/logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build: 
      context: ./frontend
      args:
        - VITE_API_URL=http://44.212.209.159:8000
    container_name: hibid-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      backend:
        condition: service_healthy
EOF
```

### Step 6: Build and Deploy

```bash
cd /opt/hibid-email-mvp

# Create necessary directories
mkdir -p data logs

# Build images
docker-compose -f docker-compose.prod.yml build

# Start containers
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 7: Verify It's Working

```bash
# Check health
curl http://localhost:8000/health

# Check containers
docker ps

# Check logs if issues
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
```

## Alternative: Fix Network Connectivity

If EC2 Instance Connect doesn't work, the issue might be:

1. **Instance in private subnet** - Needs NAT Gateway
2. **Security group misconfiguration** - Check inbound rules
3. **Network ACL blocking** - Check VPC settings

To check and fix:

```bash
# Check security group
aws ec2 describe-security-groups --group-ids sg-0f925667ae6070c4a

# Check subnet (should be public)
aws ec2 describe-subnets --subnet-ids subnet-0ec51c4b01051563c --query 'Subnets[0].[SubnetId,MapPublicIpOnLaunch]'
```

## Quick Commands Reference

Once connected via EC2 Instance Connect:

```bash
# View logs
docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml logs -f

# Restart services
docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml restart

# Stop services
docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml down

# Start services
docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml up -d

# Check status
docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml ps
```

## Application URLs (Once Running)

- **Frontend**: http://44.212.209.159:3000
- **Backend**: http://44.212.209.159:8000
- **Health Check**: http://44.212.209.159:8000/health
- **API Docs**: http://44.212.209.159:8000/docs

## Need Help?

If you're stuck:
1. Check the troubleshooting guide: `TROUBLESHOOTING.md`
2. Check AWS CloudWatch logs for the instance
3. Verify security group allows ports 22, 80, 3000, 8000 from 0.0.0.0/0

