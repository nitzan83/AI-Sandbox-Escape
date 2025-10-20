FROM python:3.9-slim-bullseye

WORKDIR /app

# --- INTENTIONAL MISCONFIGURATION ---
# The rest of the Dockerfile remains the same. The misconfiguration is still
# that we do NOT create or switch to a non-root user.
# ------------------------------------

# Copy agent code and its requirements
# The Docker build context is the project's root directory
COPY agent/ /app/agent/

# Install the agent's Python dependencies
RUN pip install --no-cache-dir -r agent/requirements.txt

# Set the default command to run when the container starts
CMD ["python", "agent/main.py"]