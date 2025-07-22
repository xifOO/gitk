import os
import shutil
import subprocess
from typing import Any, List


class SafeGitRunner:

    def __init__(self) -> None:
        self.git_path = self._get_git_path()
        self._validate_git_path()

    @staticmethod
    def _get_git_path() -> str:
        path = shutil.which("git")
        if path is None:
            raise RuntimeError("git executable not found in PATH")
        return path

    def _validate_git_path(self) -> None:
        if not self.git_path:
            raise ValueError("Git path cannot be empty")

        if not os.path.isabs(self.git_path):
            raise ValueError("Git path must be absolute")

        if not os.path.exists(self.git_path):
            raise ValueError("Git executable not found at path")

        if not os.access(self.git_path, os.X_OK):
            raise ValueError("Git executable is not executable")

        executable_name = os.path.basename(self.git_path).lower()
        if executable_name not in ("git", "git.exe"):
            raise ValueError("Executable must be git")

    def run(self, command: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
        full_command = [self.git_path] + command

        check = kwargs.pop("check", False)

        process = subprocess.Popen(  # noqa: S603
            full_command,
            stdout=kwargs.get("stdout", subprocess.PIPE),
            stderr=kwargs.get("stderr", subprocess.PIPE),
            text=kwargs.get("text", False),
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["stdout", "stderr", "text", "capture_output"]
            },
        )

        stdout, stderr = process.communicate()

        result: subprocess.CompletedProcess = subprocess.CompletedProcess(
            args=full_command,
            returncode=process.returncode,
            stdout=stdout,
            stderr=stderr,
        )

        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, full_command, stdout, stderr
            )

        return result
