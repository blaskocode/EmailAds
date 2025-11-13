#!/bin/bash

##################################################
# HiBid Email MVP - Update Deployment Script
# This script helps deploy/update the application
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

# Load deployment config
if [ -f "deployment-config.env" ]; then
    source deployment-config.env
else
    log_error "deployment-config.env not found!"
    exit 1
fi

log_info "HiBid Email MVP - Deployment Update"
log_info "Instance: $INSTANCE_ID"
log_info "Elastic IP: $ELASTIC_IP"
echo ""

#############################################
# Step 1: Check Instance Status
#############################################
log_info "Checking instance status..."
INSTANCE_STATE=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].State.Name' \
    --output text)

log_info "Instance state: $INSTANCE_STATE"

if [ "$INSTANCE_STATE" != "running" ]; then
    log_warn "Instance is not running. Starting instance..."
    aws ec2 start-instances --instance-ids $INSTANCE_ID
    log_info "Waiting for instance to start..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    log_info "Instance is now running. Waiting 30 seconds for initialization..."
    sleep 30
fi

#############################################
# Step 2: Update Security Group (if needed)
#############################################
log_info "Checking security group rules..."
MY_IP=$(curl -s ifconfig.me)
log_info "Your current IP: $MY_IP"

# Check if rule exists
EXISTING_RULE=$(aws ec2 describe-security-groups \
    --group-ids $SECURITY_GROUP_ID \
    --query "SecurityGroups[0].IpPermissions[?FromPort==\`22\`].IpRanges[?CidrIp==\`${MY_IP}/32\`]" \
    --output text)

if [ -z "$EXISTING_RULE" ]; then
    log_info "Adding SSH access from your IP..."
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 22 \
        --cidr ${MY_IP}/32 2>/dev/null || log_warn "Rule may already exist"
else
    log_info "SSH access already configured for your IP"
fi

#############################################
# Step 3: Test SSH Connection
#############################################
log_info "Testing SSH connection..."
if ssh -i $KEY_FILE -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@$ELASTIC_IP "echo 'SSH connection successful'" 2>/dev/null; then
    log_info "SSH connection successful!"
else
    log_error "SSH connection failed. Trying alternative methods..."
    
    # Try AWS Systems Manager
    log_info "Attempting to use AWS Systems Manager..."
    if aws ssm describe-instance-information --filters "Key=InstanceIds,Values=$INSTANCE_ID" --query 'InstanceInformationList[0]' --output text 2>/dev/null | grep -q "Online"; then
        log_info "SSM is available. You can connect using:"
        echo "  aws ssm start-session --target $INSTANCE_ID"
        echo ""
        log_warn "Please connect via SSM and run the deployment commands manually."
        exit 1
    else
        log_error "SSM is not available. Please check:"
        echo "  1. Instance IAM role has SSM permissions"
        echo "  2. SSM agent is installed on the instance"
        echo "  3. Network connectivity to the instance"
        echo ""
        log_info "Alternative: Use AWS Console EC2 Instance Connect or check network settings"
        exit 1
    fi
fi

#############################################
# Step 4: Upload Application Code
#############################################
log_info "Uploading application code..."
scp -i $KEY_FILE -r ./backend ./frontend ubuntu@$ELASTIC_IP:/tmp/hibid-email-mvp-update/

log_info "Code uploaded. Deploying on instance..."

#############################################
# Step 5: Deploy on Instance
#############################################
ssh -i $KEY_FILE ubuntu@$ELASTIC_IP << 'ENDSSH'
    set -e
    
    APP_DIR="/opt/hibid-email-mvp"
    UPDATE_DIR="/tmp/hibid-email-mvp-update"
    
    echo "[INFO] Creating app directory if needed..."
    sudo mkdir -p $APP_DIR
    sudo chown ubuntu:ubuntu $APP_DIR
    
    echo "[INFO] Backing up existing deployment..."
    if [ -d "$APP_DIR/backend" ]; then
        sudo cp -r $APP_DIR/backend $APP_DIR/backend.backup.$(date +%Y%m%d_%H%M%S) || true
    fi
    if [ -d "$APP_DIR/frontend" ]; then
        sudo cp -r $APP_DIR/frontend $APP_DIR/frontend.backup.$(date +%Y%m%d_%H%M%S) || true
    fi
    
    echo "[INFO] Copying new code..."
    sudo cp -r $UPDATE_DIR/backend $APP_DIR/
    sudo cp -r $UPDATE_DIR/frontend $APP_DIR/
    sudo chown -R ubuntu:ubuntu $APP_DIR
    
    echo "[INFO] Checking for .env file..."
    if [ ! -f "$APP_DIR/.env" ]; then
        echo "[WARN] .env file not found. You may need to create it."
    fi
    
    cd $APP_DIR
    
    echo "[INFO] Building Docker images..."
    docker-compose -f docker-compose.prod.yml build || {
        echo "[INFO] docker-compose.prod.yml not found, creating it..."
        # Create docker-compose.prod.yml if it doesn't exist
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
        docker-compose -f docker-compose.prod.yml build
    }
    
    echo "[INFO] Stopping existing containers..."
    docker-compose -f docker-compose.prod.yml down || true
    
    echo "[INFO] Starting containers..."
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "[INFO] Waiting for services to be healthy..."
    sleep 10
    
    echo "[INFO] Checking container status..."
    docker-compose -f docker-compose.prod.yml ps
    
    echo "[INFO] Testing health endpoint..."
    curl -f http://localhost:8000/health || echo "[WARN] Health check failed"
    
    echo "[INFO] Deployment complete!"
ENDSSH

#############################################
# Step 6: Verify Deployment
#############################################
log_info "Verifying deployment..."
sleep 5

if curl -s -f http://$ELASTIC_IP:8000/health > /dev/null; then
    log_info "✅ Backend is responding!"
else
    log_warn "⚠️  Backend health check failed"
fi

if curl -s -f http://$ELASTIC_IP:3000 > /dev/null; then
    log_info "✅ Frontend is responding!"
else
    log_warn "⚠️  Frontend may still be starting..."
fi

echo ""
log_info "========================================"
log_info "Deployment Update Complete!"
log_info "========================================"
echo ""
echo "Application URLs:"
echo "  Frontend: http://$ELASTIC_IP:3000"
echo "  Backend:  http://$ELASTIC_IP:8000"
echo "  Health:   http://$ELASTIC_IP:8000/health"
echo ""
echo "To check logs:"
echo "  ssh -i $KEY_FILE ubuntu@$ELASTIC_IP"
echo "  docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml logs -f"
echo ""

