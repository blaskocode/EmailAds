# AWS Deployment - Quick Start Guide

**Total Time to Production:** 30-60 minutes  
**Skill Level Required:** Intermediate  
**Prerequisites:** AWS account, AWS CLI configured, OpenAI API key

---

## 🚀 Three-Step Deployment

### Step 1: Run AWS Infrastructure Setup (15-20 minutes)
```bash
# On your local machine
chmod +x setup-aws.sh
./setup-aws.sh
```

**What this does:**
- Creates S3 bucket with CORS and lifecycle policies
- Sets up IAM roles and policies
- Launches EC2 instance (t3.medium)
- Configures security group
- Allocates Elastic IP
- Installs Docker and dependencies on EC2

**Output:** 
- `deployment-config.env` - All resource IDs
- `deployment-summary.txt` - Access information
- `hibid-email-mvp-key.pem` - SSH key

### Step 2: Deploy Application (10-15 minutes)
```bash
# SSH to your EC2 instance
ssh -i hibid-email-mvp-key.pem ubuntu@YOUR_ELASTIC_IP

# Upload your application code (from local machine)
scp -i hibid-email-mvp-key.pem -r ./backend ./frontend ubuntu@YOUR_ELASTIC_IP:/opt/hibid-email-mvp/

# Back on EC2: Create .env file
nano /opt/hibid-email-mvp/.env

# Add your secrets:
OPENAI_API_KEY=sk-your-key-here
S3_BUCKET_NAME=your-bucket-name-from-step1
AWS_REGION=us-east-1
# ... (see AWS_DEPLOYMENT_GUIDE.md for full template)

# Run deployment script
cd /opt/hibid-email-mvp
chmod +x deploy.sh
./deploy.sh
```

**What this does:**
- Builds Docker images
- Starts frontend and backend containers
- Sets up monitoring and backup scripts
- Configures health checks

### Step 3: Configure SSL (Optional, 5-10 minutes)
```bash
# On EC2 instance
sudo certbot --nginx -d your-domain.com

# Update nginx config to proxy to Docker containers
# See AWS_DEPLOYMENT_GUIDE.md for detailed nginx configuration
```

---

## 📋 Files Overview

### Documentation
- **`AWS_DEPLOYMENT_GUIDE.md`** - Comprehensive 100+ page deployment guide
  - Detailed step-by-step instructions
  - Troubleshooting section
  - Monitoring and logging setup
  - Backup and disaster recovery
  - Security best practices
  - Cost estimation

### Automated Scripts
- **`setup-aws.sh`** - Automated AWS infrastructure setup
  - Creates all AWS resources
  - Configures permissions
  - Launches EC2 instance
  - Sets up security groups
  
- **`deploy.sh`** - Application deployment script
  - Builds Docker images
  - Deploys containers
  - Configures monitoring
  - Sets up backups

- **`teardown.sh`** - Complete cleanup script
  - Deletes ALL AWS resources
  - Removes IAM roles/policies
  - Cleans up local files
  - Use with caution!

---

## ⚡ Quick Commands

### Deployment
```bash
# Full automated setup (run from local machine)
./setup-aws.sh

# Deploy application (run on EC2)
./deploy.sh

# View deployment info
cat deployment-summary.txt
```

### Management
```bash
# SSH to instance
ssh -i hibid-email-mvp-key.pem ubuntu@YOUR_IP

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Check status
docker-compose -f docker-compose.prod.yml ps

# Manual backup
/opt/hibid-email-mvp/backup.sh
```

### Teardown
```bash
# Delete everything (from local machine)
./teardown.sh
# Type 'DELETE' to confirm
```

---

## 🎯 Access Your Application

After successful deployment:

**Frontend:** `http://YOUR_ELASTIC_IP:3000`  
**Backend API:** `http://YOUR_ELASTIC_IP:8000`  
**API Docs:** `http://YOUR_ELASTIC_IP:8000/docs`  
**Health Check:** `http://YOUR_ELASTIC_IP:8000/health`

---

## 💰 Cost Breakdown

**Monthly AWS Costs:** ~$45-50/month

- EC2 t3.medium: ~$30
- EBS 30GB: ~$2.50
- S3 storage: ~$1.15
- Data transfer: ~$9
- CloudWatch: ~$3

**Additional:** OpenAI API costs based on usage

---

## 🔧 What If Something Goes Wrong?

### 1. Setup script fails
```bash
# Check AWS CLI configuration
aws configure list

# Verify credentials
aws sts get-caller-identity

# Re-run setup (it's idempotent)
./setup-aws.sh
```

### 2. Application won't start
```bash
# Check Docker logs
docker-compose -f docker-compose.prod.yml logs

# Verify environment variables
cat /opt/hibid-email-mvp/.env

# Check if ports are available
sudo netstat -tulpn | grep -E '3000|8000'

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### 3. Can't access application
```bash
# Check security group
aws ec2 describe-security-groups --group-ids YOUR_SG_ID

# Verify instance is running
aws ec2 describe-instances --instance-ids YOUR_INSTANCE_ID

# Check health endpoint
curl http://localhost:8000/health
```

### 4. Need to start over
```bash
# Complete cleanup
./teardown.sh

# Wait 5 minutes, then re-run
./setup-aws.sh
```

---

## 📖 Detailed Documentation

For complete details, see **`AWS_DEPLOYMENT_GUIDE.md`** which includes:

- Prerequisites and tools installation
- Step-by-step AWS infrastructure setup
- S3 bucket configuration with CORS
- IAM roles and policies
- EC2 instance configuration
- SSL certificate setup (Let's Encrypt)
- Nginx reverse proxy configuration
- CloudWatch monitoring and logging
- Automated backups
- Disaster recovery procedures
- Security best practices
- Troubleshooting guide
- Maintenance tasks

---

## 🔐 Security Checklist

Before going to production:

- [ ] Restrict SSH access to your IP only
- [ ] Enable MFA on AWS account
- [ ] Rotate SSH keys regularly
- [ ] Enable S3 bucket encryption
- [ ] Set up CloudWatch alarms
- [ ] Configure VPC (for production)
- [ ] Use AWS WAF (if using ALB)
- [ ] Regular security audits
- [ ] Keep Docker images updated
- [ ] Review CloudWatch logs

---

## 🆘 Support Resources

### AWS Documentation
- EC2: https://docs.aws.amazon.com/ec2/
- S3: https://docs.aws.amazon.com/s3/
- IAM: https://docs.aws.amazon.com/iam/

### Troubleshooting
See full troubleshooting section in `AWS_DEPLOYMENT_GUIDE.md`

### Common Issues
1. **"Instance profile not found"** - Wait 10 seconds and retry
2. **"Bucket already exists"** - Choose different S3 bucket name
3. **"Health check failed"** - Check backend logs and .env file
4. **"Permission denied"** - Verify IAM role is attached to instance

---

## ⏱️ Timeline Summary

| Phase | Time | Tasks |
|-------|------|-------|
| **Setup** | 15-20 min | Run `setup-aws.sh`, create AWS resources |
| **Deploy** | 10-15 min | Upload code, run `deploy.sh` |
| **SSL** | 5-10 min | Configure SSL with Let's Encrypt (optional) |
| **Testing** | 5-10 min | Test all functionality |
| **Total** | **35-55 min** | **Full production deployment** |

---

## ✅ Post-Deployment Checklist

- [ ] Application accessible at http://YOUR_IP:3000
- [ ] Backend health check returns 200
- [ ] Can upload test campaign
- [ ] AI processing works (<5 seconds)
- [ ] Preview renders correctly
- [ ] Can download HTML
- [ ] Monitoring script running
- [ ] Backup cron job configured
- [ ] CloudWatch logs configured
- [ ] DNS pointing to Elastic IP (if using domain)
- [ ] SSL certificate installed (if using HTTPS)

---

## 🎓 Next Steps After Deployment

1. **Test the application** thoroughly
2. **Set up monitoring alerts** in CloudWatch
3. **Configure domain name** (optional)
4. **Enable HTTPS** with SSL certificate
5. **Run load testing** to verify performance
6. **Document your setup** for team
7. **Set up CI/CD** for future updates (GitHub Actions)
8. **Plan scaling strategy** as usage grows

---

**Quick Start Complete!** 🎉

You now have a production-ready HiBid Email MVP running on AWS with:
- Automated infrastructure setup
- Containerized application deployment
- Monitoring and health checks
- Automated backups
- Disaster recovery capability

For any issues, consult `AWS_DEPLOYMENT_GUIDE.md` or the troubleshooting section.

**Happy deploying!**
