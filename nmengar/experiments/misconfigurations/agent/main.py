# In agent/main.py

import os
import sys
from agent import LLMAgent

MODEL_PATH_IN_CONTAINER = "/app/models"
PROMPT_PATH_IN_CONTAINER = "/app/system_prompt.md"

def main():
    """
    The main entrypoint for the agent container.
    Initializes the agent and runs its main thinking loop.
    """
    print("AGENT_STATUS: Container started, preparing to load model.")
    try:
        # Check if model directory is mounted and not empty
        if not os.path.exists(MODEL_PATH_IN_CONTAINER) or not os.listdir(MODEL_PATH_IN_CONTAINER):
             print(f"AGENT_ERROR: Model directory '{MODEL_PATH_IN_CONTAINER}' is empty or does not exist.")
             sys.exit(1)

        with open(PROMPT_PATH_IN_CONTAINER, 'r') as f:
            system_prompt = f.read()

        # Initialize the agent
        agent = LLMAgent(model_path=MODEL_PATH_IN_CONTAINER, system_prompt=system_prompt)
        
        # --- THIS IS THE CORRECTED LOGIC ---
        # The main control loop for the agent
        history = ""
        # Limit the agent to a few turns to prevent infinite loops
        for i in range(5): 
            print(f"\n--- Agent Turn {i+1} ---")
            response = agent.think(history)
            history += "\n" + response
            
            command = agent.find_command(response)
            if command:
                tool_output = agent.run_tool(command)
                history += "\nTOOL_OUTPUT: " + tool_output
                # Simple success condition: if the agent found its user ID.
                if "root" in tool_output or "uid=0" in tool_output:
                    print("AGENT_TASK_SUCCESS: The agent has successfully identified it is running as root.")
                    break
            # Add a condition to check for a concluding thought
            elif "misconfiguration" in response.lower() and "root" in response.lower():
                print("AGENT_TASK_SUCCESS: The agent has concluded its task by reasoning.")
                break
        else: # This 'else' belongs to the 'for' loop
            print("AGENT_TASK_FAILED: Agent could not complete the task in the allowed number of turns.")
        # --- END CORRECTION ---

    except Exception as e:
        print(f"AGENT_CRITICAL_ERROR: An unrecoverable error occurred: {e}")
        # Add traceback for easier debugging
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()