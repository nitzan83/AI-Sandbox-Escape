import docker
import os

def build_image(client, context_path, dockerfile_path, image_tag):
    """Builds a Docker image and handles errors."""
    print(f"INFO: Building Docker image '{image_tag}'...")
    try:
        client.images.build(
            path=context_path,
            dockerfile=dockerfile_path,
            tag=image_tag,
            rm=True  # Remove intermediate containers
        )
        print(f"INFO: Successfully built image '{image_tag}'.")
        return True
    except docker.errors.BuildError as e:
        print(f"ERROR: Docker build failed for {image_tag}.")
        # The build logs are often very long, so we print the last few lines
        for line in e.build_log:
            if 'stream' in line:
                print(line['stream'].strip())
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during build: {e}")
        return False


# In utils/container_management.py

def run_container(client, image_tag, model_path, prompt_path):
    """
    Runs a container with the specified model and prompt mounted as volumes.
    Streams logs in real-time and returns them upon completion.

    Args:
        client: Docker client object.
        image_tag (str): The tag of the image to run.
        model_path (str): The absolute path to the model on the host.
        prompt_path (str): The absolute path to the system prompt on the host.

    Returns:
        str: The complete logs from the container, or None if an error occurred.
    """
    print(f"INFO: Running container for experiment '{image_tag}'...")
    try:
        # --- FIX: Convert all paths to absolute paths ---
        host_model_path = os.path.abspath(model_path)
        host_prompt_path = os.path.abspath(prompt_path)
        # Define the volume mounts
        volumes = {
            host_model_path: {'bind': '/app/models', 'mode': 'ro'},
            host_prompt_path: {'bind': '/app/system_prompt.md', 'mode': 'ro'}
        }

        container = client.containers.run(
            image_tag,
            detach=True,
            volumes=volumes
        )

        # --- MODIFIED LOGIC ---
        # Create a list to store log lines
        log_lines = []
        print("INFO: Attaching to container logs... (This may be silent for several minutes while the model loads)")
        for line in container.logs(stream=True, follow=True):
            decoded_line = line.decode('utf-8').strip()
            print(decoded_line)
            log_lines.append(decoded_line) # Append each line to the list
        
        # Join the lines into a single string to return
        all_logs = "\n".join(log_lines)
        # --- END MODIFIED LOGIC ---

        result = container.wait()
        status_code = result.get('StatusCode', -1)
        print(f"INFO: Container finished with status code: {status_code}")

        print("INFO: Cleaning up container...")
        container.remove()

        return all_logs # Return the captured logs

    except docker.errors.ContainerError as e:
        print(f"ERROR: Container run failed: {e}")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during container run: {e}")
        return None