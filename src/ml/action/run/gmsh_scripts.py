import subprocess
import sys
from pathlib import Path

from src.ml.action.run.subprocess import Subprocess


class GmshScripts(Subprocess):
    def __init__(self, run_path=None, input_path=None, write_mesh=False, nohup=True,
                 **kwargs):
        super().__init__(**kwargs)
        self.run_path = Path(run_path).resolve()
        self.input_path = input_path
        self.write_mesh = write_mesh
        self.nohup = nohup
        self.returncode = 0

    def post_call(self, actions=None, *args, **kwargs):
        if self.write_mesh:
            cmd = [sys.executable,
                   str(self.run_path),
                   str(Path(self.input_path).resolve())]
        else:
            cmd = [sys.executable,
                   str(self.run_path),
                   str(Path(self.input_path).resolve()),
                   '-f']
        if self.nohup and sys.platform != 'win32':
            cmd = ['nohup'] + cmd
        try:
            r = subprocess.run(args=cmd,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               check=True)
        except subprocess.CalledProcessError as e:
            self.returncode = e.returncode
        else:
            self.returncode = r.returncode
