# Create New Instance - Step by Step

## Why Create a New Instance?

The current instance (`i-0d2ed3a68d73cc750`) has network connectivity issues preventing:
- SSH access
- EC2 Instance Connect
- SSM Session Manager
- HTTP access

Creating a new instance with proper network configuration is the fastest solution.

## Quick Start

### Step 1: Run Setup Script

```bash
cd /Users/courtneyblaskovich/Documents/Projects/EmailAds
chmod +x setup-aws.sh
./setup-aws.sh
```

This script will:
- ✅ Create S3 bucket
- ✅ Set up IAM roles (with SSM enabled)
- ✅ Create security groups
- ✅ Launch new EC2 instance
- ✅ Allocate Elastic IP
- ✅ Install Docker and dependencies
- ✅ Create deployment config file

**Time:** 15-20 minutes

### Step 2: Access the New Instance

Once setup completes, you'll get:
- New instance ID
- New Elastic IP
- SSH key file location

**Access via EC2 Instance Connect:**
1. Go to AWS Console → EC2 → Instances
2. Find the new instance (search by name: `hibid-email-mvp`)
3. Click "Connect" → "EC2 Instance Connect" → "Connect"

**Or via SSM Session Manager:**
1. Go to: https://console.aws.amazon.com/systems-manager/
2. Click "Session Manager" → "Start session"
3. Select your new instance

### Step 3: Deploy Application

Once connected, run:

```bash
# Navigate to app directory
cd /opt/hibid-email-mvp

# Upload your code (from local machine in new terminal)
# Replace NEW_IP with the new Elastic IP from deployment-config.env
scp -i hibid-email-mvp-key.pem -r ./backend ./frontend ubuntu@NEW_IP:/opt/hibid-email-mvp/

# Back on the instance, create .env file
nano .env
```

Add your environment variables (see `GET_APP_RUNNING.md` for template).

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verify
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

## What About the Old Instance?

The old instance will remain running (you'll be charged for it). You can:

1. **Terminate it** (if you don't need it):
   ```bash
   aws ec2 terminate-instances --instance-ids i-0d2ed3a68d73cc750
   ```

2. **Keep it** for now (in case you need to recover data later)

3. **Create snapshot** of the EBS volume first:
   ```bash
   # Get volume ID
   VOLUME_ID=$(aws ec2 describe-volumes --filters "Name=attachment.instance-id,Values=i-0d2ed3a68d73cc750" --query 'Volumes[0].VolumeId' --output text)
   
   # Create snapshot
   aws ec2 create-snapshot --volume-id $VOLUME_ID --description "Backup before new instance"
   ```

## After Deployment

Your new instance will have:
- ✅ Proper network configuration
- ✅ SSM enabled (for Session Manager)
- ✅ Security groups configured correctly
- ✅ Docker installed and ready
- ✅ Application accessible via HTTP

## Need Help?

If the setup script fails:
1. Check AWS CLI is configured: `aws configure list`
2. Verify you have permissions to create EC2 instances
3. Check the script output for specific errors

The script is idempotent - you can run it multiple times safely.

