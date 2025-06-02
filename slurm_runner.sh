#!/bin/bash
#SBATCH --job-name="JOB_NAME"
#SBATCH --partition=a100 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:1
#SBATCH -o "OUTPUT_FOLDER"
#SBATCH -e "ERROR_LOG_FOLDER"
#SBATCH --time=2-00:00:00

MODEL_NAME="Qwen/Qwen2-72B"
# "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
# "deepseek-ai/DeepSeek-Coder-V2-Instruct"
HF_API_KEY="HF_TOKEN"

echo "Pulling Docker image..."

docker pull lmsysorg/sglang:latest

echo "Finished pulling Docker image."

docker run --init --rm --gpus all \
  --shm-size 32g \
  -v ~/.cache/huggingface:/SGL_HF_Cache \
  -v /slurm:/slurm \
  -v nobackup/HF_HOME:/nobackup/HF_HOME \
  --env "HF_TOKEN=$HF_API_KEY" \
  --env "MODEL_NAME=$MODEL_NAME" \
  --ipc=host \
  lmsysorg/sglang:latest \
  bash -c "
      set -e
      cd "/slurm/"

      echo 'Using model: \$MODEL_NAME'
      python3 python_server_runner.py \
          --model_name \"\$MODEL_NAME\"
  "
# 
cleanup() {
echo "🧹 Cleaning up..."
pkill -f "python -m sglang.serve"
}
trap cleanup EXIT
