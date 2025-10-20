import os
from agent import LLMAgent

if __name__ == "__main__":
    print("AGENT_STATUS: Container started, preparing to load model.")

    model_path = "/app/models"
    prompt_file = "/app/system_prompt.md"
    
    # Check if model files exist
    if not os.path.exists(model_path) or not os.listdir(model_path):
        print("AGENT_ERROR: Model directory '/app/model' is empty or does not exist.")
        exit(1)
        
    # Read the system prompt from the mounted file
    try:
        with open(prompt_file, 'r') as f:
            system_prompt = f.read()
    except FileNotFoundError:
        print(f"AGENT_ERROR: System prompt file not found at {prompt_file}")
        exit(1)

    # Initialize and run the agent
    agent = LLMAgent(model_path=model_path, system_prompt=system_prompt)
    agent.run()
