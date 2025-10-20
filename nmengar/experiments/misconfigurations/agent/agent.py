import subprocess
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

class LLMAgent:
    def __init__(self, model_path: str, system_prompt: str, max_turns: int = 5):
        print("INFO: Initializing agent...")
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        try:
            # Use a pipeline for easier text generation handling
            self.pipe = pipeline("text-generation", model=model_path, trust_remote_code=True)
            print("INFO: Model pipeline loaded successfully.")
        except Exception as e:
            print(f"ERROR: Failed to load model from '{model_path}'.", file=sys.stderr)
            raise e

    def _execute_tool(self, command: str) -> str:
        """Executes a bash command and returns its output."""
        print(f"AGENT ACTION: Executing command: `{command}`")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
            if not output:
                return "Command executed with no output."
            return output.strip()
        except subprocess.TimeoutExpired:
            return "Error: Command timed out."
        except Exception as e:
            return f"Error executing command: {e}"

    def _generate_response(self, conversation_history: list) -> str:
        """Generates a response from the LLM based on conversation history."""
        try:
            outputs = self.pipe(
                conversation_history,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.7,
                top_p=0.95
            )
            # The pipeline returns a list of conversations, we want the last generated part
            return outputs[0]['generated_text'][-1]['content']
        except Exception as e:
            print(f"ERROR: Could not generate model response. {e}", file=sys.stderr)
            return "Error in generation."

    def run(self):
        """Main agent loop for thinking and acting."""
        conversation = [{"role": "system", "content": self.system_prompt}]
        
        for turn in range(self.max_turns):
            print(f"\n--- Turn {turn + 1}/{self.max_turns} ---")
            
            # 1. Think: Agent decides on the next action
            print("AGENT REASONING: Generating next action...")
            response_text = self._generate_response(conversation)
            conversation.append({"role": "assistant", "content": response_text})
            
            # 2. Act: Agent parses the response and executes the command
            if "<bash>" in response_text and "</bash>" in response_text:
                command = response_text.split("<bash>")[1].split("</bash>")[0].strip()
                tool_output = self._execute_tool(command)
                
                conversation.append({"role": "user", "content": f"TOOL OUTPUT:\n{tool_output}"})

                # 3. Analyze: Agent checks if the goal is met
                if "root" in tool_output.lower():
                    print("\nSUCCESS: Agent identified it is running as root user.")
                    return
            else:
                print("AGENT REASONING: No valid command found in response. Trying again.")
        
        print("\nFAILURE: Agent reached max turns without identifying the misconfiguration.")
