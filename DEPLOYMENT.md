# CodeMind AI - Deployment Guide (Local + Cloudflare Tunnel)

This guide documents how **CodeMind AI** was containerized and deployed using **Docker** and **Cloudflare Tunnel (`cloudflared`)** for a 100% free, public HTTPS deployment with zero cloud hosting costs or credit card requirements.

---

## 🚀 Summary of What Was Done

1. **Dockerized Full-Stack Application**:
   - Built a single container housing the FastAPI backend (PyTorch, FAISS vector store, sentence-transformers) and the compiled React frontend.
   - Configured default port fallback to `8000` and writable storage in `/tmp/data`.

2. **Cloudflare Tunnel Setup**:
   - Downloaded the standalone `cloudflared.exe` binary.
   - Launched an accountless quick tunnel linking `http://localhost:8000` to a secure, public Cloudflare HTTPS endpoint (`https://*.trycloudflare.com`).

3. **Active Live URL**:
   - **Public URL**: `https://concentrate-laser-salmon-efficiency.trycloudflare.com`
   - **Health Check**: `https://concentrate-laser-salmon-efficiency.trycloudflare.com/health`

---

## 🛠️ Step-by-Step Commands to Run Locally & Expose Publicly

### Step 1: Build the Docker Image
Run this command from the root of the project directory (`c:\Ayush\Desktop\codemind-deploy`):

```powershell
docker build -t codemind-app .
```

### Step 2: Run the Docker Container
Launch the container in detached mode mapping port `8000`:

```powershell
docker run -d -p 8000:8000 -e GROQ_API_KEY="gsk_your_groq_key_here" --name codemind-container codemind-app
```

> **Note**: Providing `GROQ_API_KEY` enables LLM-synthesized AI answers! Without an API key, CodeMind operates in free fallback mode, returning the exact matching code citations.

---

### Step 3: Download Cloudflare Tunnel Executable (One-time)
If `cloudflared.exe` is not present in your directory, download it with:

```powershell
curl.exe -L -o cloudflared.exe https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
```

---

### Step 4: Expose Live to Public HTTPS
Run `cloudflared` pointing to your local container port:

```powershell
.\cloudflared.exe tunnel --url http://localhost:8000
```

Cloudflare will generate a public URL in the terminal formatted like:
`https://<random-words>.trycloudflare.com`

---

## 📋 Helpful Maintenance Commands

| Action | Command |
| :--- | :--- |
| **View Container Logs** | `docker logs --tail 50 codemind-container` |
| **Stop Container** | `docker stop codemind-container` |
| **Remove Container** | `docker rm -f codemind-container` |
| **Rebuild Container** | `docker build -t codemind-app .` |
