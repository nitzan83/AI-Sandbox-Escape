import os
import sys
from agent import LLMAgent

MODEL_PATH_IN_CONTAINER = "/models"
PROMPT_PATH_IN_CONTAINER = "/app/system_prompt.md"

if __name__ == "__main__":
    print("--- Container Agent Starting ---")
    
    try:
        with open(PROMPT_PATH_IN_CONTAINER, 'r') as f:
            system_prompt = f.read()
    except FileNotFoundError:
        print(f"FATAL: System prompt file not found at '{PROMPT_PATH_IN_CONTAINER}'.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(MODEL_PATH_IN_CONTAINER) or not os.listdir(MODEL_PATH_IN_CONTAINER):
        print(f"FATAL: Model directory '{MODEL_PATH_IN_CONTAINER}' is missing or empty.", file=sys.stderr)
        sys.exit(1)

    try:
        agent = LLMAgent(
            model_path=MODEL_PATH_IN_CONTAINER,
            system_prompt=system_prompt
        )
        agent.run()
    except Exception as e:
        print(f"FATAL: An error occurred during agent execution: {e}", file=sys.stderr)
        sys.exit(1)

    print("--- Container Agent Finished ---")
