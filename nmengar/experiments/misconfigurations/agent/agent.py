# In agent/agent.py

import os
from ctransformers import AutoModelForCausalLM
import subprocess

class LLMAgent:
    def __init__(self, model_path, system_prompt):
        """Initializes the agent by loading the GGUF model."""
        print("INFO: Initializing agent with ctransformers for GGUF model...")
        self.system_prompt = system_prompt
        
        # GGUF models are single files. We need to find the specific .gguf file.
        gguf_file = None
        for file in os.listdir(model_path):
            if file.endswith(".gguf"):
                gguf_file = os.path.join(model_path, file)
                break
        
        if not gguf_file:
            raise FileNotFoundError("ERROR: Could not find a .gguf file in the model directory.")

        print(f"INFO: Found GGUF model file: {os.path.basename(gguf_file)}")

        try:
            # Load the GGUF model using the ctransformers library
            self.llm = AutoModelForCausalLM.from_pretrained(
                gguf_file,
                model_type="llama", # Specify model type for better performance
                context_length=4096 
            )
            print("INFO: Model loaded successfully.")
        except Exception as e:
            print(f"ERROR: Failed to load model from '{gguf_file}'.")
            raise e

    def run_tool(self, command):
        """Executes a shell command and returns the output."""
        print(f"AGENT_ACTION: Executing command -> {command}")
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            output = result.stdout + result.stderr
            print(f"TOOL_OUTPUT: {output.strip()}")
            return output.strip()
        except Exception as e:
            error_message = f"Error executing command: {e}"
            print(f"TOOL_ERROR: {error_message}")
            return error_message

    def think(self, history):
        """Generates a response from the LLM based on history."""
        full_prompt = self.system_prompt + "\n" + history
        print("AGENT_STATUS: Generating response...")
        # ctransformers model is called directly like a function
        response_text = self.llm(full_prompt, max_new_tokens=150, temperature=0.2)
        print(f"AGENT_THOUGHT: {response_text}")
        return response_text

    def find_command(self, text):
        """Parses the LLM's response to find a command."""
        if "<bash>" in text and "</bash>" in text:
            start = text.find("<bash>") + len("<bash>")
            end = text.find("</bash>")
            command = text[start:end].strip()
            return command
        return None