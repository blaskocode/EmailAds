# How to Find Your EC2 Instance in AWS Console

## Instance Details

- **Instance ID**: `i-0d2ed3a68d73cc750`
- **Name**: `hibid-email-mvp`
- **Status**: Running
- **Region**: **us-east-1** (N. Virginia)
- **Elastic IP**: 44.212.209.159
- **Availability Zone**: us-east-1a (or similar)

## Step-by-Step: Find Your Instance

### Step 1: Go to the Correct Region

**CRITICAL**: Make sure you're in the **us-east-1 (N. Virginia)** region!

1. Open AWS Console: https://console.aws.amazon.com/ec2/
2. Look at the top-right corner for the region selector
3. Click it and select: **US East (N. Virginia) us-east-1**

### Step 2: Navigate to EC2 Instances

1. In the AWS Console, search for "EC2" or go to Services → EC2
2. In the left sidebar, click **"Instances"** (under "Instances")
3. You should see a list of all your instances

### Step 3: Find Your Instance

**Option A: Search by Name**
1. In the search box at the top, type: `hibid-email-mvp`
2. The instance should appear

**Option B: Search by Instance ID**
1. In the search box, type: `i-0d2ed3a68d73cc750`
2. The instance should appear

**Option C: Filter by Tag**
1. Click the filter icon (funnel icon)
2. Select "Tags" → "Name"
3. Enter: `hibid-email-mvp`

**Option D: Look for the IP**
1. Look for an instance with Public IP: `44.212.209.159`

### Step 4: Clear Any Filters

If you still don't see it:
1. Click "Clear filters" or remove all filter tags
2. Make sure no status filters are applied
3. Refresh the page (F5 or Cmd+R)

## Quick Access Links

**Direct link to EC2 Instances in us-east-1:**
https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#Instances:

**Direct link to your specific instance (if you have access):**
https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#InstanceDetails:instanceId=i-0d2ed3a68d73cc750

## Verify You're in the Right Account

The instance is in AWS Account: `971422717446`

To verify:
1. Click your username in the top-right
2. Check the account ID matches

## If You Still Can't See It

1. **Check IAM Permissions**: You need `ec2:DescribeInstances` permission
2. **Check Multiple Accounts**: Make sure you're logged into the correct AWS account
3. **Try AWS CLI**: Run this command to verify:
   ```bash
   aws ec2 describe-instances --instance-ids i-0d2ed3a68d73cc750 --region us-east-1
   ```

## Once You Find It

1. **Select the instance** (check the box next to it)
2. **Click "Connect"** button at the top
3. **Choose "EC2 Instance Connect"** tab
4. **Click "Connect"** - This opens a browser terminal!

Then follow the steps in `GET_APP_RUNNING.md` to deploy your application.

