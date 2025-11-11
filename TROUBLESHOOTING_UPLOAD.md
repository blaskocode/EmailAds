# Troubleshooting Upload 500 Error

## Quick Diagnosis

The upload endpoint is returning a 500 error. Here's how to diagnose and fix it:

## Step 1: Check Backend Logs

The improved error handling should now show specific error messages. Check your backend logs:

**If using Docker:**
```bash
docker-compose logs backend --tail=100
```

**If running directly:**
Check the console where you started the backend server.

Look for error messages like:
- "Failed to upload logo to S3: ..."
- "Failed to create campaign: ..."
- "Error uploading campaign: ..."

## Step 2: Run Diagnostic Script

```bash
cd backend
python3 check_setup.py
```

This will check:
- ✅ Environment variables are set
- ✅ Database directory is writable
- ✅ S3 connection (if boto3 is available)
- ✅ OpenAI API key format

## Step 3: Common Issues and Fixes

### Issue: S3 Connection Failed

**Symptoms:**
- Error: "Failed to upload logo to S3: ..."
- Error: "NoCredentialsError" or "AccessDenied"

**Fixes:**
1. Verify AWS credentials in `backend/.env`:
   ```bash
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-bucket-name
   ```

2. Verify S3 bucket exists:
   ```bash
   aws s3 ls s3://your-bucket-name
   ```

3. Check IAM permissions - user needs:
   - `s3:PutObject`
   - `s3:GetObject`
   - `s3:ListBucket`

### Issue: Database Error

**Symptoms:**
- Error: "Failed to create campaign: ..."
- Error: "database is locked" or "no such table"

**Fixes:**
1. Check database directory permissions:
   ```bash
   ls -la data/
   chmod 664 data/campaigns.db  # if exists
   ```

2. Ensure database directory exists:
   ```bash
   mkdir -p data
   ```

3. Restart backend to reinitialize database

### Issue: Missing Environment Variables

**Symptoms:**
- Error: "Failed to upload campaign: ..."
- Configuration errors on startup

**Fixes:**
1. Ensure `backend/.env` file exists
2. Verify all required variables are set:
   - `OPENAI_API_KEY`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `S3_BUCKET_NAME`
   - `AWS_REGION`

### Issue: File Validation Error

**Symptoms:**
- Error: "File exceeds maximum size"
- Error: "Invalid file type"

**Fixes:**
1. Ensure logo is:
   - PNG, JPG, or JPEG format
   - Less than 5MB
   - Not empty

2. Ensure hero images (if any) are:
   - PNG, JPG, or JPEG format
   - Less than 5MB each
   - Maximum 3 files

## Step 4: Test S3 Connection Manually

If S3 is the issue, test the connection:

```python
import boto3
from app.config import settings

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

# Test bucket access
s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
print("✅ S3 connection successful!")
```

## Step 5: Check Frontend Error Display

The frontend should now display the actual error message from the server. Check:
1. Browser console (F12) for detailed error logs
2. Error message displayed on the upload page
3. Network tab to see the actual API response

## Step 6: Verify Backend is Running

```bash
# Check if backend is responding
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"hibid-email-mvp",...}
```

## Still Having Issues?

1. **Check backend logs** - The improved error handling will show exactly what's failing
2. **Verify environment** - Make sure you're running in the correct environment (Docker vs local)
3. **Test endpoints individually** - Use curl or Postman to test the upload endpoint directly
4. **Check file permissions** - Ensure the backend can write to the database directory

## Example: Testing Upload with curl

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "campaign_name=Test Campaign" \
  -F "advertiser_name=Test Advertiser" \
  -F "logo=@/path/to/logo.png" \
  -F "subject_line=Test Subject"
```

This will show the exact error message if something fails.

