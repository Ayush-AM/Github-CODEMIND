# CodeMind AI - Production Deployment Guide (AWS Elastic Beanstalk)

This guide documents how **CodeMind AI** is containerized and deployed to **AWS Elastic Beanstalk** as a production full-stack application on Docker.

---

## 🚀 Live Production Environment

- **Live Application URL**: [http://codemind-prod.ap-south-1.elasticbeanstalk.com/](http://codemind-prod.ap-south-1.elasticbeanstalk.com/)
- **Health Check Endpoint**: [http://codemind-prod.ap-south-1.elasticbeanstalk.com/health](http://codemind-prod.ap-south-1.elasticbeanstalk.com/health)
- **AWS Region**: `ap-south-1` (Mumbai)
- **Platform**: `64bit Amazon Linux 2023 v4.13.7 running Docker`
- **Instance Profile**: `aws-elasticbeanstalk-ec2-role`
- **Instance Type**: `t3.small` (Free-tier eligible, 2 vCPUs, 2 GB RAM)

---

## 🛠️ Infrastructure & Architecture Overview

1. **Full-Stack Container Architecture**:
   - Multi-stage Docker build compiling the React frontend (`frontend/dist`) and serving it via FastAPI + Uvicorn backend on port `8000`.
   - Host port `80` routed to container port `8000` via Elastic Beanstalk Nginx proxy configuration and `Dockerrun.aws.json`.

2. **Isolated Cloud Environment**:
   - Deployed under dedicated Elastic Beanstalk application (`codemind-ai`) and environment (`codemind-prod`).
   - Completely isolated from other standalone EC2 instances in the AWS account.

3. **Environment Configuration**:
   - `GROQ_API_KEY`: Configured in Elastic Beanstalk application environment settings.
   - `LLM_PROVIDER`: `groq`
   - `GROQ_MODEL`: `llama-3.3-70b-versatile`
   - `TOP_K`: `5`
   - `PORT`: `8000`
   - `CORS_ORIGINS`: `*`

---

## 📦 Deploying to Elastic Beanstalk

### Step 1: Verify `Dockerrun.aws.json`
Ensure `Dockerrun.aws.json` is present in the project root:

```json
{
  "AWSEBDockerrunVersion": "1",
  "Ports": [
    {
      "ContainerPort": 8000,
      "HostPort": 80
    }
  ]
}
```

### Step 2: Package Application Bundle
Create a zip archive containing the application code, excluding `.git`, `node_modules`, and temporary caches:

```powershell
python -c "import zipfile, os; z = zipfile.ZipFile('bundle.zip', 'w', zipfile.ZIP_DEFLATED); [z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), '.')) for r, d, files in os.walk('.') for f in files if not any(x in r for x in ['.git', 'node_modules', '__pycache__', '.venv']) and not f.endswith('.zip')]; z.close()"
```

### Step 3: Upload & Deploy via AWS CLI
```powershell
aws s3 cp bundle.zip s3://elasticbeanstalk-ap-south-1-206690614418/codemind-v1.zip
aws elasticbeanstalk create-application-version --application-name codemind-ai --version-label v1 --source-bundle S3Bucket="elasticbeanstalk-ap-south-1-206690614418",S3Key="codemind-v1.zip" --region ap-south-1
aws elasticbeanstalk update-environment --environment-name codemind-prod --version-label v1 --region ap-south-1
```

---

## 🧹 Session Cleanup & Automated Memory Management

To ensure that cloned repositories and FAISS vector indexes are not persisted indefinitely and disk space is conserved, CodeMind enforces the following automated cleanup mechanisms:

1. **Immediate Raw Code Deletion:**
   The moment a repository is successfully cloned and its vector index (FAISS) is generated, raw source files are **immediately deleted** from disk. Only lightweight generated embeddings required for question answering are retained.

2. **Inactivity Timeout (15 Minutes):**
   A background task runs continuously to monitor session activity. Repositories inactive for **15 minutes** trigger automatic purge of vector indexes and state.

3. **Automatic Cleanup on Container Shutdown:**
   When the server shuts down, a lifespan handler clears all remaining indexes and session state.

4. **Manual Wipe Endpoint:**
   To manually clear all current session data:
   ```bash
   curl -X DELETE http://codemind-prod.ap-south-1.elasticbeanstalk.com/clear
   ```

---

## 📋 Maintenance Commands

| Action | Command |
| :--- | :--- |
| **Check Live Health** | `curl -i http://codemind-prod.ap-south-1.elasticbeanstalk.com/health` |
| **View Environment Status** | `aws elasticbeanstalk describe-environments --environment-name codemind-prod --region ap-south-1` |
| **Request Environment Logs** | `aws elasticbeanstalk request-environment-info --environment-name codemind-prod --info-type tail --region ap-south-1` |
| **Retrieve Log URL** | `aws elasticbeanstalk retrieve-environment-info --environment-name codemind-prod --info-type tail --region ap-south-1` |
| **Run Container Locally** | `docker run -d -p 8000:8000 -e GROQ_API_KEY="gsk_..." codemind-app` |
