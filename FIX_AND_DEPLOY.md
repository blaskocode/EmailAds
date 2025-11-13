# Fix Network Issue and Deploy Application

## Current Problem

Both SSH and EC2 Instance Connect are failing, which indicates a network connectivity issue. I've enabled SSM (Systems Manager) on your instance, but if that doesn't work, we need to create a new instance.

## Solution Options

### Option 1: Try SSM Session Manager (Just Enabled)

I just added the SSM policy to your instance. Try this:

**In AWS Console:**
1. Go to: https://console.aws.amazon.com/systems-manager/
2. Click "Session Manager" in left sidebar
3. Click "Start session"
4. Select instance: `i-0d2ed3a68d73cc750`
5. Click "Start session"

**Or via AWS CLI:**
```bash
aws ssm start-session --target i-0d2ed3a68d73cc750
```

### Option 2: Use AWS Run Command (Remote Execution)

If SSM Session Manager doesn't work, we can execute commands remotely:

```bash
# Test connection
aws ssm send-command \
  --instance-ids i-0d2ed3a68d73cc750 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["echo Hello from instance && docker ps"]' \
  --query 'Command.CommandId' \
  --output text

# Get command output (replace COMMAND_ID with output above)
aws ssm get-command-invocation \
  --command-id COMMAND_ID \
  --instance-id i-0d2ed3a68d73cc750
```

### Option 3: Create New Instance (Recommended if above fails)

Since the current instance has persistent network issues, let's create a fresh one:

```bash
cd /Users/courtneyblaskovich/Documents/Projects/EmailAds

# First, let's get the current instance's EBS volume ID to preserve data
aws ec2 describe-volumes --filters "Name=attachment.instance-id,Values=i-0d2ed3a68d73cc750" --query 'Volumes[0].VolumeId' --output text

# Run setup script to create new instance
./setup-aws.sh
```

**Note:** This will create a new instance. You'll need to:
1. Update the Elastic IP association
2. Redeploy the application
3. Optionally migrate data from old instance

## Recommended: Quick Fix - Create New Instance

Since network connectivity is completely blocked, the fastest solution is to create a new instance:

### Step 1: Create New Instance

```bash
cd /Users/courtneyblaskovich/Documents/Projects/EmailAds
./setup-aws.sh
```

This will:
- Create a new EC2 instance with proper network configuration
- Set up security groups correctly
- Install Docker and dependencies
- Allocate a new Elastic IP

### Step 2: Deploy Application

Once the new instance is created, follow the deployment steps in `GET_APP_RUNNING.md`

### Step 3: Update Deployment Config

The script will create a new `deployment-config.env` file with the new instance details.

## Why This Happened

The instance appears to have a network configuration issue that's preventing:
- SSH connections (port 22)
- EC2 Instance Connect (also uses SSH)
- HTTP access (ports 3000, 8000)

Possible causes:
1. Instance in private subnet without NAT Gateway
2. Network ACL blocking connections
3. Route table misconfiguration
4. Security group rules not properly applied

## What I've Done

✅ Added SSM (Systems Manager) policy to IAM role  
✅ Verified instance is running  
✅ Checked security group configuration  
✅ Created deployment scripts  

## Next Steps

1. **Try SSM Session Manager first** (see Option 1 above)
2. **If that fails, create a new instance** using `./setup-aws.sh`
3. **Deploy the application** on the new instance

The setup script takes about 15-20 minutes and will create a properly configured instance that you can access.

