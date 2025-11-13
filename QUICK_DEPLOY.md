# Quick Deploy - Get App Running Now

## Current Situation

The existing instance has network issues. Let's create a fresh instance with proper configuration.

## Option 1: Automated Setup (Recommended)

I've updated the setup script to include SSM support. Run:

```bash
cd /Users/courtneyblaskovich/Documents/Projects/EmailAds
./setup-aws.sh
```

**Note:** The script is idempotent - it will skip resources that already exist. If you want a completely fresh setup, you may need to clean up first (see Option 2).

## Option 2: Manual Quick Setup

If the automated script has issues, here's a quick manual setup:

### Step 1: Create Instance via AWS Console

1. Go to: https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#LaunchInstanceWizard:
2. **Name**: `hibid-email-mvp-new`
3. **AMI**: Ubuntu Server 22.04 LTS
4. **Instance Type**: t3.medium
5. **Key Pair**: Create new or use existing
6. **Network Settings**:
   - ✅ Auto-assign public IP: Enable
   - Security group: Create new
     - Allow SSH (22) from My IP
     - Allow HTTP (80) from Anywhere
     - Allow HTTPS (443) from Anywhere
     - Allow Custom TCP (3000) from Anywhere
     - Allow Custom TCP (8000) from Anywhere
7. **Advanced Details** → **IAM instance profile**: Select `hibid-email-mvp-instance-profile` (if it exists)
8. **Launch Instance**

### Step 2: Allocate Elastic IP

1. Go to: EC2 → Elastic IPs
2. Click "Allocate Elastic IP address"
3. Click "Allocate"
4. Select the Elastic IP → Actions → Associate Elastic IP address
5. Select your new instance
6. Click "Associate"

### Step 3: Connect via EC2 Instance Connect

1. Go to: EC2 → Instances
2. Select your new instance
3. Click "Connect" → "EC2 Instance Connect" → "Connect"

### Step 4: Install Docker

In the EC2 Instance Connect terminal:

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for docker group to take effect
exit
```

Reconnect via EC2 Instance Connect.

### Step 5: Upload and Deploy

**From your local machine:**

```bash
cd /Users/courtneyblaskovich/Documents/Projects/EmailAds

# Get your new instance IP from AWS Console
NEW_IP="YOUR_NEW_ELASTIC_IP"

# Upload code
scp -i hibid-email-mvp-key.pem -r ./backend ./frontend ubuntu@$NEW_IP:/opt/hibid-email-mvp/
```

**Back in EC2 Instance Connect:**

```bash
cd /opt/hibid-email-mvp

# Create .env file
nano .env
```

Add:
```
OPENAI_API_KEY=sk-your-key-here
AWS_REGION=us-east-1
S3_BUCKET_NAME=hibid-email-mvp-assets-1762970982
DATABASE_URL=sqlite:////opt/hibid-email-mvp/data/campaigns.db
ENVIRONMENT=production
FRONTEND_URL=http://YOUR_NEW_IP:3000
BACKEND_URL=http://YOUR_NEW_IP:8000
```

```bash
# Create docker-compose.prod.yml
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

  frontend:
    build: 
      context: ./frontend
      args:
        - VITE_API_URL=http://YOUR_NEW_IP:8000
    container_name: hibid-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      backend:
        condition: service_healthy
EOF

# Replace YOUR_NEW_IP in docker-compose file
sed -i "s/YOUR_NEW_IP/$NEW_IP/g" docker-compose.prod.yml

# Build and deploy
mkdir -p data logs
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verify
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

## Option 3: Use Existing Resources, New Instance Only

If you want to keep S3 bucket and IAM roles but create a new instance:

```bash
# Get your existing resources
source deployment-config.env

# Launch new instance with existing IAM role
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name hibid-email-mvp-key \
  --security-group-ids $SECURITY_GROUP_ID \
  --iam-instance-profile Name=hibid-email-mvp-instance-profile \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=hibid-email-mvp-new}]"

# Get new instance ID and follow deployment steps above
```

## Quickest Path

**Recommended:** Use Option 1 (automated script) - it handles everything. If it fails due to existing resources, use Option 2 (manual via console) which is straightforward and visual.

