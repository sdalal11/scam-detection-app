# Docker Setup Guide

## Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- `.env` file configured with API keys (copy from `.env.example`)

## Quick Start

### 1. Build the Docker Image

```bash
cd backend
docker build -t scam-detection-api:latest .
```

This creates a production-ready Docker image with:
- Multi-stage build for smaller image size
- Non-root user for security
- Health check endpoint
- Optimized Python dependencies

### 2. Run the Container

#### Option A: Using `.env` file (Recommended)

```bash
docker run -d \
  --name scam-detection-api \
  --env-file .env \
  -p 8000:8000 \
  scam-detection-api:latest
```

#### Option B: Using individual environment variables

```bash
docker run -d \
  --name scam-detection-api \
  -e ELEVENLABS_API_KEY="your_key_here" \
  -e GEMINI_API_KEY="your_key_here" \
  -e BACKEND_HOST="0.0.0.0" \
  -e BACKEND_PORT="8000" \
  -p 8000:8000 \
  scam-detection-api:latest
```

### 3. Verify Container is Running

```bash
# Check container status
docker ps

# Check logs
docker logs scam-detection-api

# Test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "scam-detection-api",
  "context_items": 0
}
```

## Container Management

### Stop the Container

```bash
docker stop scam-detection-api
```

### Start the Container

```bash
docker start scam-detection-api
```

### Remove the Container

```bash
docker rm -f scam-detection-api
```

### View Logs (Real-time)

```bash
docker logs -f scam-detection-api
```

### Execute Commands Inside Container

```bash
docker exec -it scam-detection-api /bin/bash
```

## Building for Different Platforms

If deploying to a different architecture (e.g., ARM for Raspberry Pi):

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t scam-detection-api:latest .
```

## Troubleshooting

### Container Exits Immediately

Check logs:
```bash
docker logs scam-detection-api
```

Common issues:
- Missing API keys
- Port 8000 already in use
- Invalid environment variables

### Health Check Failing

```bash
# Check if app is listening on correct port
docker exec scam-detection-api netstat -tuln | grep 8000
```

### Port Already in Use

Find what's using port 8000:
```bash
lsof -i :8000
```

Use a different port:
```bash
docker run -d --name scam-detection-api --env-file .env -p 8001:8000 scam-detection-api:latest
```

## Production Deployment

### Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Tag the image
docker tag scam-detection-api:latest yourusername/scam-detection-api:latest

# Push to Docker Hub
docker push yourusername/scam-detection-api:latest
```

### Push to AWS ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag the image
docker tag scam-detection-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/scam-detection-api:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/scam-detection-api:latest
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ELEVENLABS_API_KEY` | Yes | - | ElevenLabs API key for audio transcription |
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key for LLM analysis |
| `BACKEND_HOST` | No | `0.0.0.0` | Host to bind the server to |
| `BACKEND_PORT` | No | `8000` | Port to run the server on |
| `FRONTEND_URL` | No | `http://localhost:3000` | Frontend URL for CORS |

## Security Best Practices

1. **Never commit `.env` files** - They're in `.gitignore`
2. **Use secrets management** in production (AWS Secrets Manager, HashiCorp Vault, etc.)
3. **Scan images for vulnerabilities**:
   ```bash
   docker scan scam-detection-api:latest
   ```
4. **Keep base images updated** - Rebuild regularly for security patches
5. **Use read-only filesystems** when possible:
   ```bash
   docker run -d --read-only --tmpfs /tmp --env-file .env -p 8000:8000 scam-detection-api:latest
   ```

