#!/usr/bin/env bash
# ==============================================================================
# LughaLLM - NVIDIA NIM (Inference Microservice) Deployment Script
# Optimized for NVIDIA H100 SXM5 (80GB) Tensor Core GPUs
# ==============================================================================

set -euo pipefail

NGC_API_KEY="${NGC_API_KEY:-}"
if [ -z "$NGC_API_KEY" ]; then
    echo "ERROR: NGC_API_KEY environment variable is required to pull NVIDIA NIM containers."
    echo "Export your key using: export NGC_API_KEY=your_ngc_key_here"
    exit 1
fi

echo "=========================================================="
echo " Starting LughaLLM deployment via NVIDIA NIM"
echo " Target: Meta Llama-3-8B-Instruct on NVIDIA H100 GPU"
echo "=========================================================="

# Authenticate with NVIDIA NGC Container Registry
echo "$NGC_API_KEY" | docker login nvcr.io --username '$oauthtoken' --password-stdin

# Define Cache directory for model weights
LOCAL_NIM_CACHE="${LOCAL_NIM_CACHE:-$HOME/.cache/nim}"
mkdir -p "$LOCAL_NIM_CACHE"

# Run the container with all GPUs exposed and model repository mounted
docker run -d --name lughallm-nim \
  --gpus all \
  --shm-size=16g \
  -e NGC_API_KEY="$NGC_API_KEY" \
  -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
  -u "$(id -u):$(id -g)" \
  -p 8001:8000 \
  nvcr.io/nim/meta/llama3-8b-instruct:latest

echo "NVIDIA NIM container started on port 8001."
echo "Health check endpoint: http://localhost:8001/v1/health/ready"
echo "OpenAI completions endpoint: http://localhost:8001/v1/chat/completions"
