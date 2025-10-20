

### Setup

#### Create a virtual environment named 'llm_sandbox_escape_experiments'
``` python -m venv llm_sandbox_escape_experiments ```

#### Activate the virtual environment
``` source llm_sandbox_escape_experiments/bin/activate ```

#### Install the requirements
``` pip install -r requirements.txt ```

#### When done, deactivate the virtual environment
``` deactivate ```


### Running an experiment

``` python orchestrator.py --model_type=[local|api] --model=<model_name> --experiment=<experiment_number> --logs=<log_file>```