#!/bin/bash

##################################################
# HiBid Email MVP - Application Deployment Script
# Run this on the EC2 instance after setup-aws.sh
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

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}HiBid Email MVP - Application Deploy${NC}"
echo -e "${GREEN}======================================${NC}\n"

# Configuration
APP_DIR="/opt/hibid-email-mvp"
BACKUP_DIR="$APP_DIR/backups"
LOG_DIR="$APP_DIR/logs"

# Check if running as correct user
if [ "$USER" != "ubuntu" ]; then
    log_error "This script must be run as ubuntu user"
    exit 1
fi

# Navigate to app directory
cd $APP_DIR || exit 1

#############################################
# 1. Check Prerequisites
#############################################
log_info "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Run setup-aws.sh first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed. Run setup-aws.sh first."
    exit 1
fi

log_info "Prerequisites check passed"

#############################################
# 2. Check Environment Variables
#############################################
log_info "Checking environment configuration..."

if [ ! -f "$APP_DIR/.env" ]; then
    log_error ".env file not found!"
    log_info "Please create .env file with the following variables:"
    cat << EOF

# Backend Configuration
OPENAI_API_KEY=sk-your-openai-key-here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name

# Database
DATABASE_URL=sqlite:////opt/hibid-email-mvp/data/campaigns.db

# Application Settings
ENVIRONMENT=production
FRONTEND_URL=http://YOUR_IP:3000
BACKEND_URL=http://YOUR_IP:8000

# API Configuration
API_RATE_LIMIT=100
MAX_UPLOAD_SIZE=5242880

# Logging
LOG_LEVEL=INFO

EOF
    exit 1
fi

# Source environment variables
set -a
source $APP_DIR/.env
set +a

# Validate critical variables
if [ -z "$OPENAI_API_KEY" ]; then
    log_error "OPENAI_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$S3_BUCKET_NAME" ]; then
    log_error "S3_BUCKET_NAME not set in .env file"
    exit 1
fi

log_info "Environment configuration validated"

#############################################
# 3. Backup Existing Data (if any)
#############################################
if [ -f "$APP_DIR/data/campaigns.db" ]; then
    log_info "Backing up existing database..."
    mkdir -p $BACKUP_DIR
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp $APP_DIR/data/campaigns.db $BACKUP_DIR/campaigns_${TIMESTAMP}.db
    log_info "Database backed up to: $BACKUP_DIR/campaigns_${TIMESTAMP}.db"
fi

#############################################
# 4. Create Production Docker Compose
#############################################
log_info "Creating production Docker Compose configuration..."

cat > $APP_DIR/docker-compose.prod.yml << 'EOF'
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
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build: 
      context: ./frontend
      args:
        - VITE_API_URL=${BACKEND_URL:-http://localhost:8000}
    container_name: hibid-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      backend:
        condition: service_healthy
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF

log_info "Docker Compose configuration created"

#############################################
# 5. Build Docker Images
#############################################
log_info "Building Docker images (this may take 5-10 minutes)..."

if ! docker-compose -f docker-compose.prod.yml build; then
    log_error "Docker build failed"
    exit 1
fi

log_info "Docker images built successfully"

#############################################
# 6. Stop Existing Containers
#############################################
if docker ps -a | grep -q "hibid"; then
    log_info "Stopping existing containers..."
    docker-compose -f docker-compose.prod.yml down
fi

#############################################
# 7. Start Application
#############################################
log_info "Starting application containers..."

if ! docker-compose -f docker-compose.prod.yml up -d; then
    log_error "Failed to start containers"
    log_info "Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi

log_info "Containers started successfully"

#############################################
# 8. Wait for Health Checks
#############################################
log_info "Waiting for services to be healthy..."

MAX_WAIT=120  # 2 minutes
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        log_info "Backend health check passed"
        break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    echo -n "."
done
echo ""

if [ $ELAPSED -ge $MAX_WAIT ]; then
    log_error "Backend health check failed after ${MAX_WAIT}s"
    log_info "View logs: docker-compose -f docker-compose.prod.yml logs backend"
    exit 1
fi

# Check frontend
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    log_info "Frontend is responding"
else
    log_warn "Frontend might still be starting..."
fi

#############################################
# 9. Setup Monitoring Script
#############################################
log_info "Setting up monitoring script..."

cat > $APP_DIR/monitor.sh << 'MONITOR'
#!/bin/bash
CHECK_INTERVAL=60
LOG_FILE="/opt/hibid-email-mvp/logs/uptime-monitor.log"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check backend
    BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    
    if [ "$BACKEND_STATUS" != "200" ]; then
        echo "$TIMESTAMP - ERROR: Backend health check failed (Status: $BACKEND_STATUS)" >> $LOG_FILE
        docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml restart backend
    fi
    
    # Check frontend
    FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
    
    if [ "$FRONTEND_STATUS" != "200" ]; then
        echo "$TIMESTAMP - ERROR: Frontend health check failed (Status: $FRONTEND_STATUS)" >> $LOG_FILE
        docker-compose -f /opt/hibid-email-mvp/docker-compose.prod.yml restart frontend
    fi
    
    sleep $CHECK_INTERVAL
done
MONITOR

chmod +x $APP_DIR/monitor.sh

# Start monitor in background
nohup $APP_DIR/monitor.sh > /dev/null 2>&1 &
log_info "Monitoring script started"

#############################################
# 10. Setup Backup Script
#############################################
log_info "Setting up backup script..."

cat > $APP_DIR/backup.sh << 'BACKUP'
#!/bin/bash
BACKUP_DIR="/opt/hibid-email-mvp/backups"
DB_FILE="/opt/hibid-email-mvp/data/campaigns.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

if [ -f "$DB_FILE" ]; then
    sqlite3 $DB_FILE ".backup '$BACKUP_DIR/campaigns_$TIMESTAMP.db'"
    gzip $BACKUP_DIR/campaigns_$TIMESTAMP.db
    
    # Upload to S3 if configured
    if [ ! -z "$S3_BUCKET_NAME" ]; then
        aws s3 cp $BACKUP_DIR/campaigns_$TIMESTAMP.db.gz s3://$S3_BUCKET_NAME/backups/
    fi
    
    # Keep only last 7 days
    find $BACKUP_DIR -name "campaigns_*.db.gz" -mtime +7 -delete
    
    echo "$(date): Backup completed - campaigns_$TIMESTAMP.db.gz"
fi
BACKUP

chmod +x $APP_DIR/backup.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/hibid-email-mvp/backup.sh >> /opt/hibid-email-mvp/logs/backup.log 2>&1") | crontab -

log_info "Backup script configured (runs daily at 2 AM)"

#############################################
# 11. Display Status
#############################################
echo ""
log_info "Checking container status..."
docker-compose -f docker-compose.prod.yml ps

#############################################
# 12. Get Public IP
#############################################
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

#############################################
# Summary
#############################################
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${YELLOW}Application URLs:${NC}"
echo "  Frontend: http://${PUBLIC_IP}:3000"
echo "  Backend:  http://${PUBLIC_IP}:8000"
echo "  API Docs: http://${PUBLIC_IP}:8000/docs"
echo "  Health:   http://${PUBLIC_IP}:8000/health"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs:    docker-compose -f docker-compose.prod.yml logs -f"
echo "  Restart:      docker-compose -f docker-compose.prod.yml restart"
echo "  Stop:         docker-compose -f docker-compose.prod.yml down"
echo "  Status:       docker-compose -f docker-compose.prod.yml ps"
echo "  Shell:        docker exec -it hibid-backend bash"
echo ""
echo -e "${YELLOW}Log Files:${NC}"
echo "  Application:  $LOG_DIR/backend.log"
echo "  Monitor:      $LOG_DIR/uptime-monitor.log"
echo "  Backup:       $LOG_DIR/backup.log"
echo ""
echo -e "${YELLOW}Management:${NC}"
echo "  Backup now:   $APP_DIR/backup.sh"
echo "  Monitor:      tail -f $LOG_DIR/uptime-monitor.log"
echo ""

# Create quick reference file
cat > $APP_DIR/QUICK_REFERENCE.txt << EOF
HiBid Email MVP - Quick Reference
Generated: $(date)

Application URLs:
- Frontend: http://${PUBLIC_IP}:3000
- Backend:  http://${PUBLIC_IP}:8000
- API Docs: http://${PUBLIC_IP}:8000/docs
- Health:   http://${PUBLIC_IP}:8000/health

Common Commands:
docker-compose -f docker-compose.prod.yml logs -f          # View logs
docker-compose -f docker-compose.prod.yml restart          # Restart all
docker-compose -f docker-compose.prod.yml restart backend  # Restart backend only
docker-compose -f docker-compose.prod.yml ps               # Check status
docker exec -it hibid-backend bash                          # Backend shell
docker exec -it hibid-frontend sh                           # Frontend shell

Management Scripts:
$APP_DIR/backup.sh          # Manual backup
$APP_DIR/monitor.sh         # Monitoring (runs automatically)

Log Files:
$LOG_DIR/backend.log
$LOG_DIR/uptime-monitor.log
$LOG_DIR/backup.log

Database:
$APP_DIR/data/campaigns.db

Backups:
$APP_DIR/backups/

Update Application:
1. cd $APP_DIR
2. git pull  # if using git
3. docker-compose -f docker-compose.prod.yml build
4. docker-compose -f docker-compose.prod.yml up -d

Rollback:
1. docker-compose -f docker-compose.prod.yml down
2. Restore database from: $BACKUP_DIR/
3. Redeploy previous version

Troubleshooting:
- Check logs: docker-compose -f docker-compose.prod.yml logs
- Check disk space: df -h
- Check memory: free -h
- Check processes: htop
- Restart services: docker-compose -f docker-compose.prod.yml restart
EOF

log_info "Quick reference saved to: $APP_DIR/QUICK_REFERENCE.txt"
echo ""
log_info "Deployment script completed successfully!"
