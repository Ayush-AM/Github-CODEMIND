---
type: "query"
date: "2026-06-10T09:51:38.730216+00:00"
question: "Why did AWS Elastic Beanstalk run out of disk space during deployment?"
contributor: "graphify"
---

# Q: Why did AWS Elastic Beanstalk run out of disk space during deployment?

## Answer

Standard PyTorch installs heavy CUDA binaries (4.5GB). Optimized requirements.txt to pull the CPU-only version (150MB) via --extra-index-url https://download.pytorch.org/whl/cpu and torch==2.5.1+cpu.