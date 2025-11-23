# ☁️ Cloud Deployment Branch - Ready to Deploy!

Welcome to the `cloud-deploy` branch! This branch contains everything you need to deploy the Kuramoto-Sivashinsky simulator to Google Cloud Platform.

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup GCP
```bash
./setup-gcp.sh
```
This script will configure your Google Cloud project automatically.

### Step 2: Add GitHub Secrets
The script will display three secrets to add to your GitHub repository:
1. Go to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`
2. Add the three secrets shown by the setup script

### Step 3: Deploy
```bash
git push origin cloud-deploy
```
That's it! GitHub Actions will automatically deploy to Cloud Run.

---

## 📚 Documentation

- **[CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)** - Complete deployment guide (19KB)
- **[QUICK_START_CLOUD.md](QUICK_START_CLOUD.md)** - Quick reference
- **[CLOUD_DEPLOY_SUMMARY.md](CLOUD_DEPLOY_SUMMARY.md)** - Implementation details

---

## 🎯 What's Included

### Containerization
- ✅ **Dockerfile** - Multi-stage build (~400MB image)
- ✅ **docker-compose.yml** - Local testing
- ✅ **wsgi.py** - Production entry point
- ✅ **Health checks** - Automatic monitoring

### CI/CD Pipelines (GitHub Actions)
- ✅ **Cloud Run** - Automatic deployment (recommended)
- ✅ **App Engine** - Manual deployment
- ✅ **Compute Engine** - Manual deployment

### Configuration
- ✅ **app.yaml** - App Engine Standard
- ✅ **app.flexible.yaml** - App Engine Flexible
- ✅ **setup-gcp.sh** - Automated GCP setup

### Security
- ✅ **Workload Identity Federation** - No keys needed
- ✅ **Non-root container** - Enhanced security
- ✅ **Shell injection protected** - Quoted variables
- ✅ **CodeQL passed** - No vulnerabilities

---

## 🧪 Local Testing

### Using Docker
```bash
docker build -t ks-simulator .
docker run -p 8080:8080 ks-simulator
```

### Using Docker Compose
```bash
docker compose up
```

Access at: http://localhost:8080

---

## 🌐 Deployment Options

### Option 1: Cloud Run (Recommended) 🌟
- **Cost**: $5-20/month (pay-per-use)
- **Deployment**: Automatic on push
- **Scaling**: Auto (0-10 instances)
- **Best for**: Serverless, variable traffic

**Setup**:
1. Run `./setup-gcp.sh`
2. Add GitHub secrets
3. Push to `cloud-deploy` branch

### Option 2: App Engine
- **Cost**: $10-30/month
- **Deployment**: Manual trigger
- **Scaling**: Managed
- **Best for**: Traditional web apps

**Deploy**:
1. Go to GitHub Actions
2. Select "Deploy to App Engine"
3. Click "Run workflow"

### Option 3: Compute Engine
- **Cost**: $7-50+/month
- **Deployment**: Manual trigger
- **Scaling**: Manual
- **Best for**: Full VM control

**Deploy**:
1. Go to GitHub Actions
2. Select "Deploy to Compute Engine"
3. Click "Run workflow"

---

## 📁 File Structure

```
.
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Local development
├── wsgi.py                       # Production entry
├── app.yaml                      # App Engine Standard
├── app.flexible.yaml             # App Engine Flexible
├── setup-gcp.sh                  # Automated setup
├── CLOUD_DEPLOYMENT.md           # Full guide (19KB)
├── QUICK_START_CLOUD.md          # Quick reference
├── CLOUD_DEPLOY_SUMMARY.md       # Implementation summary
└── .github/workflows/            # CI/CD pipelines
    ├── deploy-cloud-run.yml      # Cloud Run
    ├── deploy-app-engine.yml     # App Engine
    └── deploy-compute-engine.yml # Compute Engine
```

---

## ✅ Testing Status

All components tested and working:

| Component | Status | Notes |
|-----------|--------|-------|
| Docker Build | ✅ PASS | Multi-stage, optimized |
| Container Startup | ✅ PASS | Gunicorn running |
| Health Check | ✅ PASS | Python urllib |
| Docker Compose | ✅ PASS | Orchestration works |
| Security Scan | ✅ PASS | CodeQL clean |
| Shell Script | ✅ PASS | No injection risks |

---

## 🔒 Security Features

1. **Workload Identity Federation** - No service account keys
2. **Non-root user** - Container runs as `ksuser` (UID 1000)
3. **Minimal image** - Only necessary files included
4. **Quoted variables** - No shell injection vulnerabilities
5. **HTTPS** - Enabled by default on Cloud Run/App Engine
6. **IAM** - Principle of least privilege

---

## 💰 Cost Estimate

| Service | Monthly | Scaling | Recommendation |
|---------|---------|---------|----------------|
| **Cloud Run** | $5-20 | Auto (0-∞) | ⭐ **Recommended** |
| App Engine | $10-30 | Managed | Good for steady traffic |
| Compute Engine | $7-50+ | Manual | Full control needed |

*Cloud Run includes a generous free tier*

---

## 🛠️ Troubleshooting

### Build Issues
```bash
# Test locally
docker build -t ks-simulator .
docker run -p 8080:8080 ks-simulator
```

### Deployment Issues
- ✅ Check GitHub Actions logs
- ✅ Verify GCP APIs are enabled
- ✅ Confirm GitHub secrets are set
- ✅ Review service account permissions

### Runtime Issues
```bash
# View logs
docker logs <container-id>

# Or in GCP
gcloud run services logs read ks-simulator --region=us-central1
```

---

## 📖 Detailed Guides

### For Complete Instructions
See [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md) for:
- Step-by-step GCP setup
- Workload Identity Federation guide
- Manual deployment procedures
- Monitoring and maintenance
- Security best practices
- Cost optimization tips

### For Quick Reference
See [QUICK_START_CLOUD.md](QUICK_START_CLOUD.md) for:
- 5-minute setup
- Common commands
- Quick troubleshooting

### For Implementation Details
See [CLOUD_DEPLOY_SUMMARY.md](CLOUD_DEPLOY_SUMMARY.md) for:
- Architecture overview
- Technical decisions
- Testing results
- File descriptions

---

## 🎓 Learning Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [App Engine Documentation](https://cloud.google.com/appengine/docs)
- [Compute Engine Documentation](https://cloud.google.com/compute/docs)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/actions)

---

## 🆘 Support

### Documentation
- **Full Guide**: [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)
- **Quick Start**: [QUICK_START_CLOUD.md](QUICK_START_CLOUD.md)
- **Summary**: [CLOUD_DEPLOY_SUMMARY.md](CLOUD_DEPLOY_SUMMARY.md)

### GCP Console
- [Cloud Console](https://console.cloud.google.com/)
- [IAM & Admin](https://console.cloud.google.com/iam-admin)
- [Cloud Run](https://console.cloud.google.com/run)
- [Logs Explorer](https://console.cloud.google.com/logs)

### Community
- [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-platform)
- [GCP Slack](https://googlecloud-community.slack.com/)
- [GitHub Discussions](https://github.com/RiccardoRubini93/Kuramoto-Sivashinsky/discussions)

---

## ✨ What's Next?

1. ✅ Run `./setup-gcp.sh`
2. ✅ Add GitHub secrets
3. ✅ Push to `cloud-deploy` branch
4. ✅ Access your deployed app!
5. 📊 Set up monitoring
6. 🔔 Configure alerts
7. 🌐 Add custom domain (optional)
8. 🔐 Configure authentication (optional)

---

## 🎉 Success Checklist

Before deploying, ensure:

- [ ] GCP project created with billing enabled
- [ ] `gcloud` CLI installed and authenticated
- [ ] Docker installed (for local testing)
- [ ] GitHub repository secrets configured
- [ ] Local Docker build successful
- [ ] Local container tested
- [ ] Documentation reviewed

---

## 📝 Summary

This branch provides:
- ✅ Complete containerization of the KS simulator
- ✅ Three cloud deployment options (Cloud Run, App Engine, Compute Engine)
- ✅ Automated CI/CD pipelines via GitHub Actions
- ✅ Security best practices (Workload Identity Federation, non-root user)
- ✅ Comprehensive documentation (19KB+ of guides)
- ✅ Automated setup tools
- ✅ Local testing with Docker/Docker Compose
- ✅ All tests passing, CodeQL clean

**You're ready to deploy! 🚀**

---

*For detailed instructions, see [CLOUD_DEPLOYMENT.md](CLOUD_DEPLOYMENT.md)*
