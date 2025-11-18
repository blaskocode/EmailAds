# Successful Deployment Guide - HiBid Email MVP

**Last Successful Deployment:** November 12, 2025  
**Deployment Method:** AWS Systems Manager (SSM) Run Command  
**Instance:** i-05f785a26aaaf9f30  
**Status:** ✅ Production Running

---

## Overview

This document details the successful deployment process using AWS Systems Manager (SSM) Run Command, which was used when SSH and EC2 Instance Connect were unavailable due to network connectivity issues.

---

## Deployment Architecture

### Instance Details
- **Instance ID:** `i-05f785a26aaaf9f30`
- **Public IP:** `98.84.19.141` (Note: Not an Elastic IP - will change if instance restarts)
- **Region:** us-east-1
- **Instance Type:** t3.medium
- **AMI:** Ubuntu 22.04 LTS
- **S3 Bucket:** `hibid-email-mvp-assets-1762999536`
- **Security Group:** `sg-0f925667ae6070c4a`

### Application URLs
- **Frontend:** http://98.84.19.141:3000
- **Backend API:** http://98.84.19.141:8000
- **API Docs:** http://98.84.19.141:8000/docs
- **Health Check:** http://98.84.19.141:8000/health

---

## Why SSM Run Command?

### Problem Encountered
- SSH connections timed out
- EC2 Instance Connect failed with "Error establishing SSH connection"
- Network connectivity issues prevented direct access

### Solution
Used **AWS Systems Manager (SSM) Run Command** to execute commands remotely without SSH. This method:
- ✅ Works when SSH is blocked
- ✅ Uses IAM roles (no SSH keys needed)
- ✅ Secure and auditable
- ✅ Can execute commands on running instances

### Prerequisites
- Instance must have SSM agent installed (pre-installed on Ubuntu 22.04)
- IAM role must have `AmazonSSMManagedInstanceCore` policy attached
- Instance must be in "Online" status in SSM

---

## Deployment Process

### Step 1: Verify Instance and SSM Status

```bash
# Check instance status
aws ec2 describe-instances \
  --instance-ids i-05f785a26aaaf9f30 \
  --query 'Reservations[0].Instances[0].[InstanceId,State.Name,PublicIpAddress]' \
  --output table

# Verify SSM is available
aws ssm describe-instance-information \
  --filters "Key=InstanceIds,Values=i-05f785a26aaaf9f30" \
  --query 'InstanceInformationList[0].[PingStatus,PlatformType]' \
  --output table
```

**Expected Output:**
- Instance state: `running`
- SSM PingStatus: `Online`

### Step 2: Prepare Application Code

```bash
cd /Users/courtneyblaskovich/Documents/Projects/EmailAds

# Create compressed archive of application code
tar -czf app-code.tar.gz backend frontend

# Upload to S3
aws s3 cp app-code.tar.gz s3://hibid-email-mvp-assets-1762999536/app-code.tar.gz

# Generate presigned URL for download
aws s3 presign s3://hibid-email-mvp-assets-1762999536/app-code.tar.gz --expires-in 3600
```

### Step 3: Create Application Directory on Instance

```bash
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /opt && sudo mkdir -p hibid-email-mvp && sudo chown ubuntu:ubuntu hibid-email-mvp && echo Directory created"]' \
  --query 'Command.CommandId' \
  --output text)

# Wait and check status
sleep 3
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'Status' \
  --output text
```

### Step 4: Download and Extract Code

```bash
# Use presigned URL from Step 2
PRESIGNED_URL="https://hibid-email-mvp-assets-1762999536.s3.us-east-1.amazonaws.com/app-code.tar.gz?..."

COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"cd /opt/hibid-email-mvp && curl -L '$PRESIGNED_URL' -o app-code.tar.gz && tar -xzf app-code.tar.gz && rm app-code.tar.gz && echo 'Files extracted' && ls -la\"]" \
  --query 'Command.CommandId' \
  --output text)

# Wait and check output
sleep 10
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query '[Status,StandardOutputContent]' \
  --output text
```

### Step 5: Create Environment Variables File

```bash
# Create .env file content
cat > /tmp/env-file.txt << 'EOF'
OPENAI_API_KEY=sk-proj-your-key-here
AWS_REGION=us-east-1
S3_BUCKET_NAME=hibid-email-mvp-assets-1762999536
DATABASE_URL=sqlite:////opt/hibid-email-mvp/data/campaigns.db
ENVIRONMENT=production
FRONTEND_URL=http://98.84.19.141:3000
BACKEND_URL=http://98.84.19.141:8000
ALLOWED_ORIGINS=http://98.84.19.141:3000,http://localhost:3000
API_RATE_LIMIT=100
MAX_UPLOAD_SIZE=5242880
LOG_LEVEL=INFO
EOF

# Base64 encode and send to instance
ENV_CONTENT=$(cat /tmp/env-file.txt | base64)

COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"cd /opt/hibid-email-mvp && echo '$ENV_CONTENT' | base64 -d > .env && chmod 600 .env && echo '.env created'\"]" \
  --query 'Command.CommandId' \
  --output text)

sleep 5
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'Status' \
  --output text
```

### Step 6: Create Docker Compose File

```bash
# Create docker-compose.prod.yml content
cat > /tmp/docker-compose.yml << 'EOF'
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
        - VITE_API_URL=http://98.84.19.141:8000
    container_name: hibid-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      backend:
        condition: service_healthy
EOF

# Base64 encode and send
DOCKER_COMPOSE=$(cat /tmp/docker-compose.yml | base64)

COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"cd /opt/hibid-email-mvp && echo '$DOCKER_COMPOSE' | base64 -d > docker-compose.prod.yml && echo 'docker-compose.prod.yml created'\"]" \
  --query 'Command.CommandId' \
  --output text)

sleep 5
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'Status' \
  --output text
```

### Step 7: Build Docker Images

```bash
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /opt/hibid-email-mvp && mkdir -p data logs && docker-compose -f docker-compose.prod.yml build 2>&1 | tail -20"]' \
  --query 'Command.CommandId' \
  --output text)

echo "Building Docker images... Command ID: $COMMAND_ID"
echo "This takes 5-10 minutes. Monitor with:"
echo "aws ssm get-command-invocation --command-id $COMMAND_ID --instance-id i-05f785a26aaaf9f30 --query 'Status' --output text"

# Wait and check periodically
for i in {1..12}; do
  STATUS=$(aws ssm get-command-invocation \
    --command-id $COMMAND_ID \
    --instance-id i-05f785a26aaaf9f30 \
    --query 'Status' \
    --output text 2>/dev/null)
  echo "Status check $i: $STATUS"
  if [ "$STATUS" = "Success" ] || [ "$STATUS" = "Failed" ]; then
    break
  fi
  sleep 30
done

# Get final output
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query '[Status,StandardOutputContent]' \
  --output text | tail -30
```

### Step 8: Start Containers

```bash
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /opt/hibid-email-mvp && docker-compose -f docker-compose.prod.yml up -d && sleep 5 && docker-compose -f docker-compose.prod.yml ps"]' \
  --query 'Command.CommandId' \
  --output text)

sleep 10
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query '[Status,StandardOutputContent]' \
  --output text
```

### Step 9: Verify Deployment

```bash
# Test health endpoint
curl http://98.84.19.141:8000/health

# Test frontend
curl -I http://98.84.19.141:3000

# Check containers via SSM
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["docker ps --format \"table {{.Names}}\t{{.Status}}\t{{.Ports}}\""]' \
  --query 'Command.CommandId' \
  --output text)

sleep 5
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'StandardOutputContent' \
  --output text
```

---

## Updating the Application

### Method 1: Update Single Files (Recommended for Code Changes)

```bash
cd /Users/courtneyblaskovich/Documents/Projects/EmailAds

# Example: Update a Python file
FILE_CONTENT=$(cat backend/app/routes/approve.py | base64)

COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"cd /opt/hibid-email-mvp/backend/app/routes && echo '$FILE_CONTENT' | base64 -d > approve.py && echo 'File updated'\"]" \
  --query 'Command.CommandId' \
  --output text)

sleep 5
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'Status' \
  --output text

# Restart backend to apply changes
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /opt/hibid-email-mvp && docker-compose -f docker-compose.prod.yml restart backend"]' \
  --query 'Command.CommandId' \
  --output text)

sleep 10
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'Status' \
  --output text
```

### Method 2: Full Application Update

```bash
cd /Users/courtneyblaskovich/Documents/Projects/EmailAds

# Create new archive
tar -czf app-code-update.tar.gz backend frontend

# Upload to S3
aws s3 cp app-code-update.tar.gz s3://hibid-email-mvp-assets-1762999536/app-code-update.tar.gz

# Get presigned URL
PRESIGNED_URL=$(aws s3 presign s3://hibid-email-mvp-assets-1762999536/app-code-update.tar.gz --expires-in 3600 --output text)

# Download and extract on instance
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"cd /opt/hibid-email-mvp && curl -L '$PRESIGNED_URL' -o app-code-update.tar.gz && tar -xzf app-code-update.tar.gz && rm app-code-update.tar.gz && echo 'Code updated'\"]" \
  --query 'Command.CommandId' \
  --output text)

sleep 10
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'Status' \
  --output text

# Rebuild and restart
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /opt/hibid-email-mvp && docker-compose -f docker-compose.prod.yml build && docker-compose -f docker-compose.prod.yml up -d"]' \
  --query 'Command.CommandId' \
  --output text)

# Monitor build (takes 5-10 minutes)
for i in {1..12}; do
  STATUS=$(aws ssm get-command-invocation \
    --command-id $COMMAND_ID \
    --instance-id i-05f785a26aaaf9f30 \
    --query 'Status' \
    --output text 2>/dev/null)
  echo "Status: $STATUS"
  if [ "$STATUS" = "Success" ] || [ "$STATUS" = "Failed" ]; then
    break
  fi
  sleep 30
done
```

---

## Common Operations

### View Container Logs

```bash
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /opt/hibid-email-mvp && docker-compose -f docker-compose.prod.yml logs --tail=50 backend"]' \
  --query 'Command.CommandId' \
  --output text)

sleep 5
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'StandardOutputContent' \
  --output text
```

### Restart Services

```bash
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /opt/hibid-email-mvp && docker-compose -f docker-compose.prod.yml restart"]' \
  --query 'Command.CommandId' \
  --output text)

sleep 5
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'Status' \
  --output text
```

### Check Container Status

```bash
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["docker ps --format \"table {{.Names}}\t{{.Status}}\t{{.Ports}}\""]' \
  --query 'Command.CommandId' \
  --output text)

sleep 3
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'StandardOutputContent' \
  --output text
```

### Update Environment Variables

```bash
# Create updated .env content
cat > /tmp/env-updated.txt << 'EOF'
OPENAI_API_KEY=sk-new-key-here
AWS_REGION=us-east-1
S3_BUCKET_NAME=hibid-email-mvp-assets-1762999536
# ... (other variables)
EOF

ENV_CONTENT=$(cat /tmp/env-updated.txt | base64)

COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"cd /opt/hibid-email-mvp && echo '$ENV_CONTENT' | base64 -d > .env && chmod 600 .env && docker-compose -f docker-compose.prod.yml restart backend\"]" \
  --query 'Command.CommandId' \
  --output text)

sleep 10
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'Status' \
  --output text
```

---

## Troubleshooting

### SSM Command Not Working

**Problem:** Commands return "Failed" or timeout

**Solutions:**
1. Check SSM agent status:
   ```bash
   aws ssm describe-instance-information \
     --filters "Key=InstanceIds,Values=i-05f785a26aaaf9f30" \
     --query 'InstanceInformationList[0].PingStatus' \
     --output text
   ```
   Should return: `Online`

2. Verify IAM role has SSM permissions:
   ```bash
   aws iam list-attached-role-policies \
     --role-name hibid-email-mvp-ec2-role \
     --query 'AttachedPolicies[*].PolicyArn' \
     --output text
   ```
   Should include: `arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore`

3. Check instance is running:
   ```bash
   aws ec2 describe-instances \
     --instance-ids i-05f785a26aaaf9f30 \
     --query 'Reservations[0].Instances[0].State.Name' \
     --output text
   ```

### Container Won't Start

**Problem:** Docker containers fail to start

**Solution:**
```bash
# Check logs
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /opt/hibid-email-mvp && docker-compose -f docker-compose.prod.yml logs backend"]' \
  --query 'Command.CommandId' \
  --output text)

sleep 5
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'StandardOutputContent' \
  --output text
```

### Application Not Accessible

**Problem:** Can't reach frontend or backend

**Solutions:**
1. Check security group allows ports 3000 and 8000:
   ```bash
   aws ec2 describe-security-groups \
     --group-ids sg-0f925667ae6070c4a \
     --query 'SecurityGroups[0].IpPermissions[?FromPort==`3000` || FromPort==`8000`]' \
     --output json
   ```

2. Verify containers are running:
   ```bash
   # Use the "Check Container Status" command above
   ```

3. Test from instance itself:
   ```bash
   COMMAND_ID=$(aws ssm send-command \
     --instance-ids i-05f785a26aaaf9f30 \
     --document-name "AWS-RunShellScript" \
     --parameters 'commands=["curl -f http://localhost:8000/health && curl -I http://localhost:3000"]' \
     --query 'Command.CommandId' \
     --output text)
   ```

### Base64 Encoding Issues

**Problem:** Large files fail to encode/send

**Solution:** Use S3 upload method instead:
```bash
# Upload file to S3
aws s3 cp backend/app/routes/approve.py s3://hibid-email-mvp-assets-1762999536/approve.py

# Download on instance
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /opt/hibid-email-mvp && aws s3 cp s3://hibid-email-mvp-assets-1762999536/approve.py backend/app/routes/approve.py"]' \
  --query 'Command.CommandId' \
  --output text)
```

---

## Key Learnings

### What Worked Well
1. ✅ **SSM Run Command** - Reliable when SSH unavailable
2. ✅ **S3 + Presigned URLs** - Efficient for file transfers
3. ✅ **Base64 encoding** - Works for small to medium files
4. ✅ **Docker Compose** - Consistent deployment environment
5. ✅ **Health checks** - Automatic container restart on failure

### Best Practices
1. **Always verify SSM status** before attempting deployment
2. **Use presigned URLs** for large file transfers (more reliable than base64)
3. **Monitor command status** with polling loops
4. **Check container logs** when troubleshooting
5. **Update .env file** when environment variables change
6. **Restart containers** after code changes

### Limitations
1. **Base64 encoding** has size limits (~50KB practical limit)
2. **SSM commands** have timeout limits (default 3600 seconds)
3. **No interactive debugging** - can't step through code
4. **Command output** may be truncated for very long outputs

---

## Quick Reference Commands

### Get Instance Info
```bash
aws ec2 describe-instances \
  --instance-ids i-05f785a26aaaf9f30 \
  --query 'Reservations[0].Instances[0].[InstanceId,State.Name,PublicIpAddress]' \
  --output table
```

### Check SSM Status
```bash
aws ssm describe-instance-information \
  --filters "Key=InstanceIds,Values=i-05f785a26aaaf9f30" \
  --query 'InstanceInformationList[0].[PingStatus,LastPingDateTime]' \
  --output table
```

### Send SSM Command
```bash
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["YOUR_COMMAND_HERE"]' \
  --query 'Command.CommandId' \
  --output text)

# Check status
aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query '[Status,StandardOutputContent]' \
  --output text
```

### Upload File to S3
```bash
aws s3 cp local-file.txt s3://hibid-email-mvp-assets-1762999536/file.txt
```

### Generate Presigned URL
```bash
aws s3 presign s3://hibid-email-mvp-assets-1762999536/file.txt --expires-in 3600
```

---

## Alternative: SSM Session Manager

If you prefer an interactive session (like SSH), you can use SSM Session Manager:

```bash
# Start interactive session
aws ssm start-session --target i-05f785a26aaaf9f30

# Then run commands interactively:
cd /opt/hibid-email-mvp
docker-compose -f docker-compose.prod.yml logs -f
# etc.
```

**Note:** Requires AWS Session Manager plugin installed:
```bash
# macOS
brew install --cask session-manager-plugin

# Or download from:
# https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html
```

---

## Deployment Checklist

### Initial Deployment
- [ ] Verify instance is running
- [ ] Check SSM is online
- [ ] Upload code to S3
- [ ] Create application directory
- [ ] Download and extract code
- [ ] Create .env file
- [ ] Create docker-compose.prod.yml
- [ ] Build Docker images
- [ ] Start containers
- [ ] Verify health endpoints
- [ ] Test frontend and backend

### Code Updates
- [ ] Upload changed files to S3 or encode as base64
- [ ] Update files on instance
- [ ] Restart affected containers
- [ ] Verify changes are applied
- [ ] Check logs for errors

### Environment Updates
- [ ] Update .env file
- [ ] Restart containers to load new variables
- [ ] Verify configuration is correct

---

## Important Notes

1. **Public IP vs Elastic IP:** Current instance uses public IP (`98.84.19.141`) which will change if instance stops. Consider associating an Elastic IP for production.

2. **CORS Configuration:** Make sure `ALLOWED_ORIGINS` in `.env` includes the frontend URL.

3. **Database Persistence:** Database is stored at `/opt/hibid-email-mvp/data/campaigns.db` and persists across container restarts.

4. **Logs Location:** Application logs are at `/opt/hibid-email-mvp/logs/` on the instance.

5. **Backup:** Database backups should be configured (see `backup.sh` script in deployment).

---

## Success Metrics

✅ **Deployment Time:** ~15-20 minutes for full deployment  
✅ **Update Time:** ~5-10 minutes for code updates  
✅ **Reliability:** SSM Run Command is more reliable than SSH when network issues exist  
✅ **Zero Downtime:** Container restarts are quick (< 30 seconds)

---

**Document Created:** November 12, 2025  
**Last Updated:** November 12, 2025  
**Deployment Method:** SSM Run Command  
**Status:** Production Running ✅

