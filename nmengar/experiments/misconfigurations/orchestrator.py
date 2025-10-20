import argparse
from utils.get_model import get_model_path
from utils.container_management import build_image, run_container
import os
import sys
import docker

def main(model_name: str, experiment_number: str):
    """
    Orchestrates a single experiment run.
    """
    print(f"--- Starting Orchestration for Experiment {experiment_number} ---")
    
    # 1. Ensure the model is available on the host
    token_file_path = './api_keys/huggingface.txt'
    host_model_path = get_model_path(model_name, token_file_path)
    if not host_model_path:
        print("ERROR: Orchestration failed. Model could not be found or downloaded.", file=sys.stderr)
        sys.exit(1)

    # 2. Define experiment-specific paths
    experiment_dir = f"containers/experiment{experiment_number}"
    dockerfile_path = os.path.join(experiment_dir, "Dockerfile")
    host_prompt_path = os.path.join(experiment_dir, "system_prompt.md")
    image_tag = f"misconfig-exp-{experiment_number}:latest"
    
    if not os.path.exists(dockerfile_path) or not os.path.exists(host_prompt_path):
        print(f"ERROR: Experiment {experiment_number} is not configured correctly. Missing files.", file=sys.stderr)
        sys.exit(1)

    # 3. Initialize Docker client
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        print("ERROR: Docker is not running. Please start Docker Desktop and try again.", file=sys.stderr)
        sys.exit(1)
        
    # 4. Build the Docker image (using project root '.' as context)
    if not build_image(client, context_path='.', dockerfile_path=dockerfile_path, image_tag=image_tag):
        sys.exit(1)

    # 5. Run the container
    logs = run_container(client, image_tag, host_model_path, host_prompt_path)
    
    # 6. Parse and report the final result
    print("\n--- Final Logs Analysis ---")
    if logs:
        print(logs.strip())
        print("--------------------------\n")
        if "SUCCESS:" in logs:
            print(f"RESULT: Experiment {experiment_number} SUCCEEDED. Misconfiguration identified.")
        else:
            print(f"RESULT: Experiment {experiment_number} FAILED.")
    else:
        print(f"RESULT: Experiment {experiment_number} FAILED TO PRODUCE LOGS.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_type', type=str, help='Local model or model via API', required=True)
    parser.add_argument('--model_name', type=str, help='Model Name to be used for the experiment', required=True)
    parser.add_argument('--experiment', type=str, help='Experiment Number to be run', required=True)
    args_in = parser.parse_args()
    # TODO @nmengar: Add API-based model functionality
    # token_file_path = './api_keys/huggingface.txt'
    main(args_in.model_name, args_in.experiment)