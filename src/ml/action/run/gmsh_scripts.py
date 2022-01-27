import subprocess
import sys
from pathlib import Path

from src.ml.action.action import Action


class GmshScripts(Action):
    def __init__(self, tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None,
                 run_path=None, input_path=None, write_mesh=False, nohup=True):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.run_path = Path(run_path).resolve()
        self.input_path = input_path
        self.write_mesh = write_mesh
        self.nohup = nohup

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            super().__call__(*args, **kwargs)
            if self.write_mesh:
                cmd = [sys.executable,
                       str(self.run_path),
                       str(Path(self.input_path).resolve())]
            else:
                cmd = [sys.executable,
                       str(self.run_path),
                       str(Path(self.input_path).resolve()),
                       '-f']
            if self.nohup:
                cmd = ['nohup'] + cmd
            r = subprocess.run(args=cmd,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               check=True)
            return r

        if self.episode is not None:
            return self.episode(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)
