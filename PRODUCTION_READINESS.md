# Production Readiness Checklist

This document outlines the requirements and checks needed before deploying HiBid Email MVP to production.

---

## ✅ Pre-Deployment Checklist

### Infrastructure

- [ ] **AWS Resources Configured**
  - [ ] S3 bucket created with proper CORS configuration
  - [ ] IAM roles and policies set up with least privilege
  - [ ] EC2 instance or ECS cluster configured
  - [ ] Security groups configured (ports 80, 443, 8000, 3000)
  - [ ] Elastic IP allocated (if using EC2)
  - [ ] VPC and subnets configured (recommended for production)

- [ ] **Database**
  - [ ] SQLite database file has proper permissions
  - [ ] Database backup strategy in place
  - [ ] Consider migration to PostgreSQL/RDS for production scale

- [ ] **Storage**
  - [ ] S3 bucket has lifecycle policies configured
  - [ ] S3 bucket encryption enabled
  - [ ] S3 bucket versioning enabled (optional)
  - [ ] S3 bucket access logging enabled

### Security

- [ ] **Credentials & Secrets**
  - [ ] All secrets stored in environment variables (not in code)
  - [ ] `.env` file excluded from version control
  - [ ] AWS credentials use IAM roles (not access keys in code)
  - [ ] OpenAI API key stored securely
  - [ ] Secrets rotation plan in place

- [ ] **Access Control**
  - [ ] SSH access restricted to specific IPs
  - [ ] MFA enabled on AWS account
  - [ ] IAM users follow least privilege principle
  - [ ] API endpoints secured (consider adding authentication for production)

- [ ] **Network Security**
  - [ ] HTTPS enabled with valid SSL certificate
  - [ ] Security groups restrict unnecessary ports
  - [ ] CORS configured for specific origins (not `*` in production)
  - [ ] Rate limiting implemented (recommended)

### Application Configuration

- [ ] **Environment Variables**
  - [ ] All required environment variables set
  - [ ] `LOG_LEVEL` set to `INFO` or `WARNING` (not `DEBUG`)
  - [ ] `FRONTEND_URL` and `BACKEND_URL` set to production URLs
  - [ ] `ALLOWED_ORIGINS` restricted to production domain

- [ ] **Docker Configuration**
  - [ ] Docker images built with production optimizations
  - [ ] Multi-stage builds used to reduce image size
  - [ ] No development dependencies in production images
  - [ ] Health checks configured in docker-compose

- [ ] **Application Settings**
  - [ ] Debug mode disabled
  - [ ] Error messages don't expose sensitive information
  - [ ] Logging configured for production
  - [ ] CORS settings appropriate for production

### Monitoring & Logging

- [ ] **Monitoring**
  - [ ] CloudWatch alarms configured
  - [ ] Application health checks configured
  - [ ] Uptime monitoring set up (e.g., UptimeRobot)
  - [ ] Performance metrics collection enabled

- [ ] **Logging**
  - [ ] Application logs sent to CloudWatch or centralized logging
  - [ ] Log retention policy configured
  - [ ] Error tracking set up (e.g., Sentry)
  - [ ] Access logs enabled

- [ ] **Alerting**
  - [ ] Alerts configured for critical errors
  - [ ] Alerts configured for high latency
  - [ ] Alerts configured for service downtime
  - [ ] On-call rotation established

### Backup & Disaster Recovery

- [ ] **Backups**
  - [ ] Database backup script configured
  - [ ] Automated backup schedule in place (daily recommended)
  - [ ] Backup retention policy defined
  - [ ] Backup restoration tested

- [ ] **Disaster Recovery**
  - [ ] Disaster recovery plan documented
  - [ ] Recovery time objective (RTO) defined
  - [ ] Recovery point objective (RPO) defined
  - [ ] Failover procedures tested

### Performance

- [ ] **Performance Testing**
  - [ ] Load testing completed
  - [ ] Proof generation time verified (<5 seconds)
  - [ ] API response times meet targets
  - [ ] Concurrent user capacity tested

- [ ] **Optimization**
  - [ ] Database queries optimized
  - [ ] Image optimization working correctly
  - [ ] Caching implemented where appropriate
  - [ ] CDN configured for static assets (if applicable)

### Testing

- [ ] **Test Coverage**
  - [ ] Backend test coverage >60%
  - [ ] Frontend test coverage >60%
  - [ ] Integration tests passing
  - [ ] End-to-end tests passing

- [ ] **Manual Testing**
  - [ ] Complete user flow tested
  - [ ] Error scenarios tested
  - [ ] Browser compatibility verified
  - [ ] Mobile responsiveness verified

### Documentation

- [ ] **Documentation Complete**
  - [ ] README.md updated with production setup
  - [ ] API documentation complete
  - [ ] Deployment guide reviewed
  - [ ] Runbook for common operations created

- [ ] **Team Knowledge**
  - [ ] Team trained on deployment process
  - [ ] Team trained on monitoring and alerting
  - [ ] Team trained on incident response
  - [ ] On-call procedures documented

---

## 🔍 Production Readiness Tests

### Functional Tests

Run these tests before deploying to production:

1. **Upload Flow**
   ```bash
   # Test file upload
   curl -X POST "https://your-domain.com/api/v1/upload" \
     -F "campaign_name=Test Campaign" \
     -F "advertiser_name=Test Advertiser" \
     -F "logo=@test-logo.png"
   ```

2. **AI Processing**
   ```bash
   # Test AI processing (should complete in <5 seconds)
   curl -X POST "https://your-domain.com/api/v1/process/{campaign_id}"
   ```

3. **Proof Generation**
   ```bash
   # Test proof generation (should complete in <2 seconds)
   curl -X POST "https://your-domain.com/api/v1/generate/{campaign_id}"
   ```

4. **Preview**
   ```bash
   # Test preview retrieval
   curl "https://your-domain.com/api/v1/preview/{campaign_id}"
   ```

5. **Approval & Download**
   ```bash
   # Test approval
   curl -X POST "https://your-domain.com/api/v1/approve/{campaign_id}" \
     -H "Content-Type: application/json" \
     -d '{"decision": "approve"}'
   
   # Test download
   curl -O -J "https://your-domain.com/api/v1/download/{campaign_id}"
   ```

### Performance Tests

1. **Response Time Tests**
   - Upload: <1 second
   - Process: <5 seconds (hard requirement)
   - Generate: <2 seconds
   - Preview: <1 second (cached) or <2 seconds (generate)
   - Approve: <1 second
   - Download: <500ms

2. **Load Tests**
   - Test with 10 concurrent users
   - Test with 50 concurrent users
   - Monitor resource usage (CPU, memory, network)

3. **Stress Tests**
   - Test with maximum file sizes (5MB images)
   - Test with multiple hero images (3 images)
   - Test with long text content

### Security Tests

1. **Input Validation**
   - Test with invalid file types
   - Test with oversized files
   - Test with malicious file names
   - Test with SQL injection attempts (if applicable)

2. **CORS Tests**
   - Verify CORS headers are correct
   - Test from unauthorized origins

3. **Error Handling**
   - Verify error messages don't expose sensitive info
   - Test error responses are properly formatted

---

## 🚨 Production Deployment Steps

### 1. Pre-Deployment

```bash
# 1. Review all checklist items
# 2. Run all tests locally
cd backend && pytest
cd frontend && npm test

# 3. Build production Docker images
docker-compose -f docker-compose.prod.yml build

# 4. Test production build locally
docker-compose -f docker-compose.prod.yml up
```

### 2. Deployment

```bash
# 1. SSH to production server
ssh -i key.pem user@production-server

# 2. Pull latest code
cd /opt/hibid-email-mvp
git pull origin main

# 3. Update environment variables if needed
nano .env

# 4. Deploy
./deploy.sh

# 5. Verify deployment
curl https://your-domain.com/health
```

### 3. Post-Deployment

```bash
# 1. Run smoke tests
./scripts/smoke-tests.sh

# 2. Check logs
docker-compose -f docker-compose.prod.yml logs -f

# 3. Monitor metrics
# Check CloudWatch dashboard

# 4. Verify all endpoints
# Run functional tests from above
```

---

## 📊 Monitoring Checklist

After deployment, verify:

- [ ] Health check endpoint returns 200
- [ ] Application logs are being collected
- [ ] CloudWatch metrics are being recorded
- [ ] Alarms are configured and working
- [ ] Error rate is within acceptable limits
- [ ] Response times meet targets
- [ ] No critical errors in logs

---

## 🔄 Maintenance Tasks

### Daily
- [ ] Review error logs
- [ ] Check application health
- [ ] Monitor resource usage

### Weekly
- [ ] Review performance metrics
- [ ] Check backup completion
- [ ] Review security logs
- [ ] Update dependencies (if needed)

### Monthly
- [ ] Review and rotate secrets
- [ ] Review and optimize costs
- [ ] Security audit
- [ ] Performance optimization review
- [ ] Disaster recovery drill

---

## 🆘 Incident Response

### When Issues Occur

1. **Check Health Endpoint**
   ```bash
   curl https://your-domain.com/health
   ```

2. **Check Logs**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

3. **Check Metrics**
   - CloudWatch dashboard
   - Application metrics

4. **Common Issues**
   - See [README.md](README.md) troubleshooting section
   - See [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) troubleshooting section

---

## 📝 Sign-Off

Before marking as production-ready:

- [ ] All checklist items completed
- [ ] All tests passing
- [ ] Performance targets met
- [ ] Security review completed
- [ ] Documentation reviewed
- [ ] Team trained

**Approved by:** _________________  
**Date:** _________________  
**Version:** 1.0.0

---

**Last Updated:** November 2025

