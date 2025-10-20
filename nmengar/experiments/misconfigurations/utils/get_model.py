import os
from huggingface_hub import snapshot_download

def read_token_from_file(file_path: str) -> str:
    """Reads a token from a specified text file."""
    if not os.path.exists(file_path):
        print(f"Token file not found at '{file_path}'.")
        return None
    try:
        with open(file_path, 'r') as f:
            # Read and strip any leading/trailing whitespace (like newlines)
            token = f.read().strip()
            return token
    except Exception as e:
        print(f"Error reading token file '{file_path}': {e}")
        return None

def get_model_path(model_name: str, token_file_path: str) -> str:
    """
    Checks if a model is present locally and downloads it if not.

    Args:
        model_name (str): The name of the model from Hugging Face Hub
                          (e.g., 'bert-base-uncased').

    Returns:
        str: The local path to the model directory.
    """
    # Define the local path for the model
    local_path = os.path.join('./models', model_name)
    token = read_token_from_file(token_file_path)

    # Check if the model directory already exists
    if os.path.isdir(local_path):
        print(f"Model '{model_name}' found locally at '{local_path}'.")
        return local_path
    else:
        print(f"Model '{model_name}' not found locally. Downloading from Hugging Face Hub...")
        # Ensure the base './models' directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Download the model from Hugging Face and save it to the specified path
        try:
            snapshot_download(
                repo_id=model_name,
                local_dir=local_path,
                token=token
            )
            print(f"Download complete. Model saved to '{local_path}'.")
            return local_path
        except Exception as e:
            print(f"Failed to download model '{model_name}'. Error: {e}")
            return None