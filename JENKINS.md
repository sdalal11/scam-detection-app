# Jenkins CI/CD Pipeline Setup Guide

## Overview

This Jenkins pipeline automates the complete CI/CD process for the Scam Detection API:

1. ✅ Checks out code from GitHub
2. ✅ Sets up Python environment
3. ✅ Runs unit tests with coverage
4. ✅ Builds Docker image
5. ✅ Tests Docker image health
6. ✅ Pushes to Docker Hub
7. ✅ Cleans up resources

## Prerequisites

### 1. Jenkins Server
- Jenkins 2.x or higher installed
- Required plugins:
  - Docker Pipeline Plugin
  - Git Plugin
  - Pipeline Plugin
  - HTML Publisher Plugin (for coverage reports)
  - JUnit Plugin (for test reports)

### 2. Server Requirements
- Docker installed on Jenkins server
- Python 3.12+ installed
- Git installed
- Network access to GitHub and Docker Hub

### 3. Credentials Required
- Docker Hub username and password/token
- GitHub credentials (if private repository)

---

## Setup Instructions

### Step 1: Install Jenkins Plugins

1. Go to: **Jenkins Dashboard → Manage Jenkins → Manage Plugins**
2. Click **Available** tab
3. Search and install:
   - Docker Pipeline
   - Docker Commons Plugin
   - HTML Publisher Plugin
   - JUnit Plugin
   - Pipeline
   - Git Plugin

### Step 2: Configure Docker Hub Credentials

1. Go to: **Jenkins Dashboard → Manage Jenkins → Manage Credentials**
2. Click **(global)** domain
3. Click **Add Credentials**
4. Configure:
   - **Kind**: Username with password
   - **Username**: `sdalal11`
   - **Password**: Your Docker Hub password or access token
   - **ID**: `dockerhub-credentials` (must match Jenkinsfile)
   - **Description**: Docker Hub credentials for sdalal11
5. Click **Create**

#### Creating Docker Hub Access Token (Recommended over password):
1. Login to Docker Hub: https://hub.docker.com
2. Go to: **Account Settings → Security → Access Tokens**
3. Click **New Access Token**
4. Name: `jenkins-pipeline`
5. Access permissions: **Read, Write, Delete**
6. Copy the token (you can't see it again!)
7. Use this token as the password in Jenkins credentials

### Step 3: Create Jenkins Pipeline Job

1. Go to **Jenkins Dashboard → New Item**
2. Enter name: `scam-detection-api-pipeline`
3. Select **Pipeline**
4. Click **OK**

### Step 4: Configure Pipeline

#### General Settings:
- ✅ Check **GitHub project**
  - Project url: `https://github.com/sdalal11/scam-detection-app/`

#### Build Triggers (Optional):
- ✅ Check **GitHub hook trigger for GITScm polling** (for automatic builds on push)
- OR ✅ Check **Poll SCM** with schedule: `H/5 * * * *` (checks every 5 minutes)

#### Pipeline Configuration:
1. **Definition**: Pipeline script from SCM
2. **SCM**: Git
3. **Repository URL**: `https://github.com/sdalal11/scam-detection-app.git`
4. **Credentials**: Add your GitHub credentials if private repo
5. **Branch Specifier**: `*/main` (or your default branch)
6. **Script Path**: `Jenkinsfile`
7. Click **Save**

### Step 5: Configure GitHub Webhook (Optional - for automatic builds)

If you want Jenkins to automatically build on every push:

1. Go to your GitHub repository: https://github.com/sdalal11/scam-detection-app
2. Click **Settings → Webhooks → Add webhook**
3. Configure:
   - **Payload URL**: `http://your-jenkins-server:8080/github-webhook/`
   - **Content type**: `application/json`
   - **Events**: Just the push event
   - **Active**: ✅
4. Click **Add webhook**

---

## Running the Pipeline

### Manual Build:
1. Go to Jenkins Dashboard
2. Click on `scam-detection-api-pipeline`
3. Click **Build Now**
4. Watch the pipeline stages execute in real-time

### Automatic Build:
- Push code to GitHub
- Jenkins automatically triggers build (if webhook configured)

---

## Pipeline Stages Explained

### 1. **Checkout** (30 seconds)
- Pulls latest code from GitHub
- Shows latest commit

### 2. **Setup Python Environment** (1-2 minutes)
- Creates virtual environment
- Installs dependencies from `requirements.txt`

### 3. **Run Tests** (30 seconds)
- Executes pytest with coverage
- Generates HTML coverage report
- Publishes test results
- **Fails pipeline if tests fail** ❌

### 4. **Build Docker Image** (2-3 minutes)
- Builds Docker image using multi-stage Dockerfile
- Tags with build number and git commit hash
- Also tags as `latest`

### 5. **Test Docker Image** (30 seconds)
- Starts container
- Checks health endpoint
- Ensures container runs properly
- Cleans up test container

### 6. **Push to Docker Hub** (1-2 minutes)
- Authenticates with Docker Hub
- Pushes tagged image
- Pushes latest image
- Available at: `docker pull sdalal11/scam-detection-api:latest`

### 7. **Cleanup Local Images** (10 seconds)
- Removes local images to save disk space
- Prunes unused Docker resources

**Total Pipeline Duration: ~5-8 minutes**

---

## Viewing Results

### Test Results:
- Go to pipeline job → Latest build
- Click **Test Result** in left sidebar
- View detailed test reports

### Coverage Report:
- Go to pipeline job → Latest build
- Click **Coverage Report** in left sidebar
- View HTML coverage with line-by-line analysis

### Console Output:
- Go to pipeline job → Latest build
- Click **Console Output**
- View detailed logs of each stage

### Docker Hub:
- View your images at: https://hub.docker.com/r/sdalal11/scam-detection-api
- See all tags and versions

---

## Using the Built Image

### Pull and Run:
```bash
# Pull the latest image
docker pull sdalal11/scam-detection-api:latest

# Run the container
docker run -d \
  --name scam-detection-api \
  -e ELEVENLABS_API_KEY="your_key" \
  -e GEMINI_API_KEY="your_key" \
  -p 8000:8000 \
  sdalal11/scam-detection-api:latest

# Check health
curl http://localhost:8000/health
```

### Pull Specific Version:
```bash
# Pull by build tag (example)
docker pull sdalal11/scam-detection-api:42-a1b2c3d

# Run specific version
docker run -d \
  --name scam-detection-api \
  -e ELEVENLABS_API_KEY="your_key" \
  -e GEMINI_API_KEY="your_key" \
  -p 8000:8000 \
  sdalal11/scam-detection-api:42-a1b2c3d
```

---

## Troubleshooting

### Pipeline Fails at "Run Tests"
**Problem**: Tests failing
**Solution**:
```bash
# Run tests locally first
cd backend
python -m pytest -v
```

### Pipeline Fails at "Push to Docker Hub"
**Problem**: Authentication failed
**Solution**:
- Verify Docker Hub credentials in Jenkins
- Use access token instead of password
- Check credential ID matches `dockerhub-credentials`

### Pipeline Fails at "Test Docker Image"
**Problem**: Port 8080 already in use
**Solution**:
- Change port in Jenkinsfile (line in Test Docker Image stage)
- Or kill process using port 8080

### Build is Slow
**Problem**: Pipeline takes too long
**Solution**:
- Use Docker layer caching
- Consider using Jenkins agents with Docker
- Optimize Dockerfile

### Workspace Issues
**Problem**: Disk space running out
**Solution**:
```bash
# On Jenkins server
docker system prune -a
docker volume prune
```

---

## Pipeline Maintenance

### Update Docker Hub Credentials:
1. Jenkins → Credentials → Update `dockerhub-credentials`

### Update Pipeline:
1. Edit `Jenkinsfile` in repository
2. Push changes to GitHub
3. Jenkins automatically uses updated Jenkinsfile

### View Pipeline History:
- Pipeline job → Build History
- See all previous builds
- Compare changes between builds

---

## Security Best Practices

1. ✅ **Use Docker Hub Access Tokens** (not passwords)
2. ✅ **Store credentials in Jenkins** (never in code)
3. ✅ **Use HTTPS for GitHub** webhooks
4. ✅ **Limit Jenkins user permissions**
5. ✅ **Regularly update Jenkins plugins**
6. ✅ **Enable Jenkins security**
7. ✅ **Use private Docker repositories** for sensitive code

---

## Next Steps

After successful pipeline runs:

### Option 1: Add Deployment Stage
Extend pipeline to deploy to production server:
- Add SSH credentials to Jenkins
- Add deployment stage to Jenkinsfile
- Deploy to EC2, DigitalOcean, or your server

### Option 2: Add Notifications
Add Slack/Email notifications:
```groovy
post {
    success {
        slackSend(color: 'good', message: "Build Successful: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
    }
    failure {
        slackSend(color: 'danger', message: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
    }
}
```

### Option 3: Multi-Environment Pipeline
- Add staging and production environments
- Use different Docker tags for each environment
- Add manual approval gates

---

## Support & Resources

- **Jenkins Documentation**: https://www.jenkins.io/doc/
- **Docker Hub**: https://hub.docker.com/r/sdalal11/scam-detection-api
- **Pipeline Syntax**: https://www.jenkins.io/doc/book/pipeline/syntax/
- **Docker Pipeline Plugin**: https://plugins.jenkins.io/docker-workflow/

---

## Summary

✅ **Step 1**: Tests - Complete
✅ **Step 2**: Docker - Complete  
✅ **Step 3**: Jenkins CI/CD - Ready to configure

**Your pipeline is production-ready and follows industry best practices!** 🚀
