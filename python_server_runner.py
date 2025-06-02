import os
import json
from openai import OpenAI
import argparse

# Argument parsing
argparser = argparse.ArgumentParser()
argparser.add_argument("--model_name", type=str, default="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")
args = argparser.parse_args()
MODEL_NAME = args.model_name

# Use SGLang if not OpenAI model
from sglang.utils import wait_for_server, print_highlight, terminate_process, launch_server_cmd

SERVER_PROCESS, PORT = launch_server_cmd(
    f"""
    python3 -m sglang.launch_server --model-path {MODEL_NAME} \
    --host 0.0.0.0 --trust-remote-code
    """
)

wait_for_server(f"http://localhost:{PORT}")

client = OpenAI(base_url=f"http://127.0.0.1:{PORT}/v1", api_key="None")

def perform_request(SYSTEM_PROMPT, PROMPT):
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": PROMPT},
            ],
            seed=42
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error in request: {e}")
        return None

SYSTEM_PROMPT = "Give code in python using basic data structures and algorithms."
PROMPT = "Write code to get the product of an array except self"

response = perform_request(SYSTEM_PROMPT, PROMPT)
if response:
    print("Response:\n", response)
    with open("/slurm/outputs/response.txt", "w") as f:
        f.write(response)


print("Response saved to response.txt")

if not "gpt" in MODEL_NAME:
    terminate_process(SERVER_PROCESS)
print("Server process terminated.")
print("All done!")
