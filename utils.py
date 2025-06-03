import os
import shlex
import subprocess


class BashFuntionCaller:
    def __init__(self, script: str, env=None):
        self.script = os.path.join(os.path.dirname(__file__), script)
        self.env = env or os.environ.copy()
    
    def __getattr__(self, name):
        def call_fun(*args):
            _arg = " ".join(shlex.quote(arg) for arg in args)
            cmd = f"source {self.script} && {name} {_arg}"
            return subprocess.check_output(
                ["bash", "-c", cmd],
                universal_newlines=True,
                stderr=subprocess.STDOUT,
                env=self.env
            )
        return call_fun