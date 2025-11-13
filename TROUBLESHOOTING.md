# Troubleshooting Deployment Access

## Current Issue: SSH Connection Timeout

The EC2 instance is running but SSH connections are timing out. Here are the solutions:

## Quick Solutions

### Option 1: Use AWS Console EC2 Instance Connect (Easiest)

1. Go to AWS Console → EC2 → Instances
2. Select instance: `i-0d2ed3a68d73cc750`
3. Click "Connect" → "EC2 Instance Connect"
4. This opens a browser-based terminal (no SSH needed)

### Option 2: Check Network Connectivity

The instance might be behind a firewall or have network restrictions. Check:

```bash
# Verify instance is running
aws ec2 describe-instances --instance-ids i-0d2ed3a68d73cc750

# Check security group (should allow SSH from 0.0.0.0/0)
aws ec2 describe-security-groups --group-ids sg-0f925667ae6070c4a

# Check if application is accessible via HTTP
curl http://44.212.209.159:8000/health
curl http://44.212.209.159:3000
```

### Option 3: Enable AWS Systems Manager (SSM)

If SSM is enabled, you can connect without SSH:

```bash
# Check if SSM is available
aws ssm describe-instance-information --filters "Key=InstanceIds,Values=i-0d2ed3a68d73cc750"

# Connect via SSM
aws ssm start-session --target i-0d2ed3a68d73cc750
```

**To enable SSM:**
1. Ensure IAM role has `AmazonSSMManagedInstanceCore` policy
2. SSM agent should be pre-installed on Ubuntu 22.04
3. Instance needs internet access to reach SSM endpoints

### Option 4: Create New Instance with Better Network Config

If the current instance has persistent network issues:

```bash
# Use the setup script to create a fresh instance
./setup-aws.sh
```

## Manual Deployment Steps (Once Connected)

Once you have access (via EC2 Instance Connect or SSM):

```bash
# 1. Navigate to app directory
cd /opt/hibid-email-mvp

# 2. Check if app exists
ls -la

# 3. If app doesn't exist, upload code:
#    From local machine:
scp -i hibid-email-mvp-key.pem -r ./backend ./frontend ubuntu@44.212.209.159:/opt/hibid-email-mvp/

# 4. Create .env file (if needed)
nano /opt/hibid-email-mvp/.env
# Add your environment variables

# 5. Deploy
cd /opt/hibid-email-mvp
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 6. Check status
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

## Current Instance Details

- **Instance ID:** i-0d2ed3a68d73cc750
- **Elastic IP:** 44.212.209.159
- **Status:** Running
- **Security Group:** sg-0f925667ae6070c4a (allows SSH from 0.0.0.0/0)
- **Region:** us-east-1

## Next Steps

1. **Try AWS Console EC2 Instance Connect** (easiest option)
2. If that works, deploy the application manually
3. If that doesn't work, check VPC/subnet routing
4. As last resort, create a new instance with `./setup-aws.sh`

## Application URLs (Once Deployed)

- Frontend: http://44.212.209.159:3000
- Backend: http://44.212.209.159:8000
- Health: http://44.212.209.159:8000/health

