# Step 3 - Jenkins CI/CD Pipeline - Setup Checklist

## ✅ Files Created

- [x] **`Jenkinsfile`** - Complete CI/CD pipeline definition
- [x] **`JENKINS.md`** - Comprehensive setup and usage guide
- [x] **`STEP3_CHECKLIST.md`** - This checklist

---

## 📋 Jenkins Server Setup

### Prerequisites:
- [ ] Jenkins server installed and running
- [ ] Jenkins accessible via web browser
- [ ] Docker installed on Jenkins server
- [ ] Python 3.12+ installed on Jenkins server
- [ ] Git installed on Jenkins server

### Quick Install (if Jenkins not installed):

#### macOS:
```bash
brew install jenkins-lts
brew services start jenkins-lts
# Access at: http://localhost:8080
```

#### Ubuntu/Linux:
```bash
# Install Java
sudo apt update
sudo apt install openjdk-11-jdk

# Install Jenkins
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update
sudo apt install jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins
# Access at: http://localhost:8080
```

#### Docker (Simplest):
```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
  
# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 🔌 Jenkins Plugins Installation

- [ ] **Docker Pipeline Plugin** - For Docker commands in pipeline
- [ ] **Docker Commons Plugin** - Docker integration
- [ ] **Git Plugin** - Git repository integration
- [ ] **Pipeline Plugin** - Pipeline functionality
- [ ] **HTML Publisher Plugin** - For coverage reports
- [ ] **JUnit Plugin** - For test reports
- [ ] **Credentials Binding Plugin** - Secure credential handling

**Install via**: Jenkins → Manage Jenkins → Manage Plugins → Available

---

## 🔐 Credentials Setup

### 1. Docker Hub Credentials
- [ ] Create Docker Hub account (if not exists): https://hub.docker.com/signup
- [ ] Generate Docker Hub access token:
  - Docker Hub → Account Settings → Security → New Access Token
  - Name: `jenkins-pipeline`
  - Permissions: Read, Write, Delete
  - **Copy the token!** (Can't see it again)
- [ ] Add to Jenkins:
  - Jenkins → Manage Jenkins → Manage Credentials
  - Click (global) → Add Credentials
  - Kind: **Username with password**
  - Username: `sdalal11`
  - Password: **[Your Docker Hub token]**
  - ID: `dockerhub-credentials`
  - Description: Docker Hub credentials
  - Click **Create**

### 2. GitHub Credentials (if private repo)
- [ ] Generate GitHub Personal Access Token (if needed)
- [ ] Add to Jenkins credentials with ID: `github-credentials`

---

## 🚀 Create Jenkins Pipeline Job

- [ ] Jenkins Dashboard → New Item
- [ ] Name: `scam-detection-api-pipeline`
- [ ] Type: **Pipeline**
- [ ] Click OK

### Configure Job:

#### General:
- [ ] Description: "CI/CD pipeline for Scam Detection API"
- [ ] ✅ GitHub project
- [ ] Project url: `https://github.com/sdalal11/scam-detection-app/`

#### Build Triggers (Choose one):
- [ ] **Poll SCM**: `H/5 * * * *` (checks every 5 minutes)
- [ ] **GitHub hook trigger** (requires webhook setup)

#### Pipeline:
- [ ] Definition: **Pipeline script from SCM**
- [ ] SCM: **Git**
- [ ] Repository URL: `https://github.com/sdalal11/scam-detection-app.git`
- [ ] Credentials: Add if private repo
- [ ] Branch Specifier: `*/main`
- [ ] Script Path: `Jenkinsfile`
- [ ] Click **Save**

---

## 🔔 GitHub Webhook (Optional - for auto-builds)

- [ ] GitHub repo → Settings → Webhooks → Add webhook
- [ ] Payload URL: `http://your-jenkins-url:8080/github-webhook/`
- [ ] Content type: `application/json`
- [ ] Events: **Just the push event**
- [ ] Active: ✅
- [ ] Click **Add webhook**

---

## 🧪 Test the Pipeline

### First Build (Manual):
- [ ] Go to pipeline job
- [ ] Click **Build Now**
- [ ] Watch console output
- [ ] Verify all stages pass:
  - [ ] ✅ Checkout
  - [ ] ✅ Setup Python Environment
  - [ ] ✅ Run Tests
  - [ ] ✅ Build Docker Image
  - [ ] ✅ Test Docker Image
  - [ ] ✅ Push to Docker Hub
  - [ ] ✅ Cleanup Local Images

### Verify Results:
- [ ] Check test results in Jenkins
- [ ] Check coverage report in Jenkins
- [ ] Verify image on Docker Hub: https://hub.docker.com/r/sdalal11/scam-detection-api
- [ ] Pull and test image locally:
  ```bash
  docker pull sdalal11/scam-detection-api:latest
  docker run -d --name test -e ELEVENLABS_API_KEY=test -e GEMINI_API_KEY=test -p 8000:8000 sdalal11/scam-detection-api:latest
  curl http://localhost:8000/health
  docker stop test && docker rm test
  ```

---

## ✅ Pipeline Verification

### Stage Timing (Expected):
- [ ] Checkout: ~30 seconds
- [ ] Setup: ~1-2 minutes
- [ ] Tests: ~30 seconds
- [ ] Build: ~2-3 minutes
- [ ] Test Image: ~30 seconds
- [ ] Push: ~1-2 minutes
- [ ] Cleanup: ~10 seconds
- **Total**: ~5-8 minutes ✅

### Expected Artifacts:
- [ ] Docker image on Docker Hub with tags:
  - `latest`
  - `{BUILD_NUMBER}-{GIT_COMMIT}`
- [ ] Test results in Jenkins
- [ ] Coverage report in Jenkins
- [ ] Console logs showing all stages

---

## 🐛 Troubleshooting

### If Pipeline Fails:

#### At "Checkout" Stage:
- [ ] Check GitHub repository URL
- [ ] Verify credentials if private repo
- [ ] Check network connectivity

#### At "Run Tests" Stage:
- [ ] Run tests locally first: `cd backend && python -m pytest -v`
- [ ] Check all dependencies installed
- [ ] Verify `.env.example` exists

#### At "Build Docker Image" Stage:
- [ ] Check Dockerfile syntax
- [ ] Verify Docker daemon running on Jenkins server
- [ ] Check Jenkins user has Docker permissions: `sudo usermod -aG docker jenkins`

#### At "Push to Docker Hub" Stage:
- [ ] Verify Docker Hub credentials
- [ ] Check credential ID is exactly `dockerhub-credentials`
- [ ] Verify access token has write permissions
- [ ] Test manual login: `docker login -u sdalal11`

#### At "Test Docker Image" Stage:
- [ ] Check port 8080 not already in use
- [ ] Verify health endpoint works locally
- [ ] Check container logs: `docker logs test-container-{BUILD_NUMBER}`

---

## 📊 Monitoring & Maintenance

### Regular Tasks:
- [ ] Monitor pipeline success rate
- [ ] Review failed builds and fix issues
- [ ] Update Jenkins plugins monthly
- [ ] Rotate Docker Hub access tokens periodically
- [ ] Clean up old Docker images from Docker Hub
- [ ] Review Jenkins disk space usage

### Pipeline Metrics to Track:
- [ ] Build success rate (aim for >95%)
- [ ] Average build time (should stay ~5-8 minutes)
- [ ] Test coverage percentage (aim for >80%)
- [ ] Failed test trends

---

## 🎯 Success Criteria

Pipeline is considered **production-ready** when:

- [x] ✅ Jenkinsfile created with all stages
- [ ] ✅ Jenkins server running
- [ ] ✅ All plugins installed
- [ ] ✅ Credentials configured
- [ ] ✅ Pipeline job created
- [ ] ✅ First build succeeds
- [ ] ✅ Tests pass
- [ ] ✅ Docker image builds
- [ ] ✅ Image pushed to Docker Hub
- [ ] ✅ Image can be pulled and runs successfully
- [ ] ✅ Documentation complete

---

## 🚀 Next Steps (Post-Setup)

### Enhancements to Consider:

1. **Add Deployment Stage**
   - Deploy to production server via SSH
   - Add staging environment
   - Implement blue-green deployment

2. **Add Notifications**
   - Slack notifications on build status
   - Email notifications for failures
   - GitHub commit status updates

3. **Improve Pipeline**
   - Parallel test execution
   - Docker layer caching
   - Separate build agents for different stages

4. **Security Enhancements**
   - Image vulnerability scanning
   - SAST/DAST integration
   - Secret scanning

5. **Monitoring**
   - Add Prometheus metrics
   - Set up Grafana dashboards
   - Application performance monitoring

---

## 📝 Notes

- Pipeline uses **Docker Hub** (not AWS ECR) as requested
- Images are tagged with build number and git commit for traceability
- Tests must pass or pipeline fails (quality gate)
- Automatic cleanup prevents disk space issues
- All secrets handled securely via Jenkins credentials

---

## 🎉 Completion

Once all items are checked:

✅ **Step 1**: Unit Tests - Complete  
✅ **Step 2**: Docker Support - Complete  
✅ **Step 3**: Jenkins CI/CD Pipeline - Complete  

**Your application is now fully productionized!** 🎊

---

## 📚 Documentation Reference

- **`Jenkinsfile`** - Pipeline definition
- **`JENKINS.md`** - Detailed setup guide
- **`DOCKER.md`** - Docker usage guide
- **`STEP2_CHECKLIST.md`** - Docker verification
- **`README.md`** - Project overview

---

**Questions or Issues?** Check `JENKINS.md` for detailed troubleshooting guide.
