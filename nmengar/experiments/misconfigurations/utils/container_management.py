import docker
import os
import sys

def build_image(client: docker.DockerClient, context_path: str, dockerfile_path: str, image_tag: str) -> bool:
    """
    Builds a Docker image from a specific Dockerfile but uses the project root as context.

    Args:
        client: The Docker client instance.
        context_path: The build context path (should be the project root '.').
        dockerfile_path: The relative path to the Dockerfile from the root.
        image_tag: The tag to apply to the built image.

    Returns:
        True on success, False on failure.
    """
    print(f"INFO: Building Docker image '{image_tag}'...")
    try:
        client.images.build(path=context_path, dockerfile=dockerfile_path, tag=image_tag, rm=True)
        return True
    except docker.errors.BuildError as e:
        print(f"ERROR: Docker build failed. Check the Dockerfile and context.", file=sys.stderr)
        for line in e.build_log:
            if 'stream' in line:
                print(line['stream'].strip(), file=sys.stderr)
        return False
    except TypeError:
        print("ERROR: Docker build failed. This might be due to an issue with the Docker daemon.", file=sys.stderr)
        return False


def run_container(client: docker.DockerClient, image_tag: str, host_model_path: str, host_prompt_path: str) -> str:
    """
    Runs the container with specified volumes and returns the logs.

    Returns:
        The container logs as a string, or None on failure.
    """
    container_model_path = "/models"
    container_prompt_path = "/app/system_prompt.md"

    print(f"INFO: Running container '{image_tag}'...")
    try:
        container = client.containers.run(
            image_tag,
            detach=True,
            volumes={
                host_model_path: {'bind': container_model_path, 'mode': 'ro'},
                host_prompt_path: {'bind': container_prompt_path, 'mode': 'ro'}
            }
        )
        # Wait for the container to finish and get the exit code
        result = container.wait()
        exit_code = result.get('StatusCode', -1)
        print(f"INFO: Container finished with exit code {exit_code}.")
        
        logs = container.logs().decode('utf-8')
        container.remove()
        return logs
    except Exception as e:
        print(f"ERROR: An error occurred during container execution: {e}", file=sys.stderr)
        return None
