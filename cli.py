import logging
import subprocess


logger = logging.Logger("logger")

def run_script(script_name, *args):
    command = ["bash", f"./scripts/{script_name}"] + list(args)
    result =  subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error(result.stderr)
    
    return result.stdout.strip()
