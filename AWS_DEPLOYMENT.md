# 🛠️ AWS Elastic Beanstalk Deployment Documentation - CodeMind AI

This document details the step-by-step process, commands used, challenges faced, and architectural optimizations implemented to host the CodeMind AI application on **AWS Elastic Beanstalk**.

---

## 🏗️ Deployment Architecture

```
Internet (HTTP Port 80)
      │
      ▼
[AWS Route 53 / DNS]
      │
      ▼
[Elastic Beanstalk Environment] (e-s3wcaxsqy2)
      │
      ▼
[EC2 Instance] (t3.small - 2GB RAM / 2 vCPUs)
      │
      ▼
[Docker Container] (FastAPI Backend + React Frontend built together)
      │ (FastAPI maps / to build assets, and serving APIs on paths)
      ▼
[LLM Provider] (Groq API)
```

---

## 📋 Steps Executed

### Phase 1: AWS Credentials & CLI Configuration
1. **IAM User Creation**:
   - Created user `codemind` on AWS Console.
   - Attached `AdministratorAccess` policy.
   - Generated **Command Line Interface (CLI)** Access Keys.
2. **Tools Installation**:
   - Installed AWS CLI (`winget install --id Amazon.AWSCLI`).
   - Installed EB CLI (`pip install awsebcli`).
3. **CLI Authentication**:
   ```powershell
   aws configure
   ```
   Inputs:
   - AWS Access Key ID: `AKIASK4OY7RWYYZCLGTY` (Rotated/Deleted post-deploy)
   - AWS Secret Access Key: `pm7zVyv...`
   - Default region name: `ap-south-1` (Mumbai)
   - Default output format: `json`
4. **Verification**:
   ```powershell
   aws sts get-caller-identity
   ```

---

### Phase 2: Codebase Optimization & Preparation

We ran into two main resource limitations when building on the AWS instance, which we optimized directly in the code:

#### 1. Disk Space Optimization (`requirements.txt`)
- **Problem**: Installing standard PyTorch (`torch`) pulled in large CUDA/GPU binaries resulting in a **4.5 GB** dependency footprint, running the EC2 instance completely out of disk space.
- **Solution**: We edited `backend/requirements.txt` to pull the CPU-only version from PyTorch's wheel index:
  ```txt
  --extra-index-url https://download.pytorch.org/whl/cpu
  torch==2.5.1+cpu
  sentence-transformers==3.3.1
  faiss-cpu==1.10.0
  numpy==2.2.3
  ...
  ```
  This reduced the package size to **~150 MB** and resolved the disk capacity issue.

#### 2. Single-Container Beanstalk Routing (`docker-compose.yml`)
- **Problem**: The codebase had a `docker-compose.yml` defining two separate containers (backend and frontend). Elastic Beanstalk saw this and launched a multi-container environment. However, neither container mapped to the host's port 80, resulting in `ERR_CONNECTION_REFUSED`.
- **Solution**: We removed `docker-compose.yml` for production. Because the FastAPI backend (`backend/app.py`) already mounts and serves the React frontend static build, we configured Beanstalk to run as a **single container**. It builds the root `Dockerfile` and maps port 80 to uvicorn on port 8000 automatically.

---

### Phase 3: Elastic Beanstalk Commands

These are the exact commands used to spin up, configure, and update the environment:

1. **Create deploy bundle and exclude junk/local files (`.ebignore`)**:
   Created `.ebignore` in the root folder containing paths to ignore (e.g. `.venv/`, `node_modules/`, `repositories/`, `indexes/`, etc.).
2. **Initialize application**:
   ```powershell
   eb init codemind-ai --platform docker --region ap-south-1
   ```
3. **Create the environment (Using Free-Tier Eligible `t3.small` instance)**:
   We initially tried `t3.medium` but it failed due to Free Tier restriction policies. We checked eligible types (`aws ec2 describe-instance-types ...`) and selected `t3.small` (2GB RAM), which is 100% Free-Tier eligible:
   ```powershell
   eb create codemind-ai-prod --instance-type t3.small --single --timeout 20 --envvars LLM_PROVIDER=groq,GROQ_API_KEY=gsk_z8Y7mWSE...,GROQ_MODEL=llama-3.3-70b-versatile,STORAGE_ROOT=/var/data,FRONTEND_DIST_DIR=/app/frontend/dist
   ```
4. **Deploy new updates**:
   After making adjustments to `requirements.txt` and removing `docker-compose.yml`, we pushed the update using:
   ```powershell
   git add .
   git commit -m "Optimize deployment"
   eb deploy
   ```
5. **Open environment**:
   ```powershell
   eb open
   ```

---

## 🔗 Live Application Endpoint

- **Frontend / Landing Page**: [http://codemind-ai-prod.eba-nc4jp4sj.ap-south-1.elasticbeanstalk.com](http://codemind-ai-prod.eba-nc4jp4sj.ap-south-1.elasticbeanstalk.com)
- **API Health check**: [http://codemind-ai-prod.eba-nc4jp4sj.ap-south-1.elasticbeanstalk.com/health](http://codemind-ai-prod.eba-nc4jp4sj.ap-south-1.elasticbeanstalk.com/health)

---

## 🔄 Routine Pipeline Maintenance

If you make modifications to CodeMind AI in the future:
1. **Commit your modifications locally**:
   ```powershell
   git add .
   git commit -m "Describe your modifications"
   ```
2. **Push updates to AWS**:
   ```powershell
   eb deploy
   ```
3. **View live server output logs** to ensure everything builds and boots correctly:
   ```powershell
   eb logs
   ```
