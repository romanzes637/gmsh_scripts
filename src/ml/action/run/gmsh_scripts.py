import subprocess
import sys
from pathlib import Path

from src.ml.action.action import Action


class GmshScripts(Action):
    def __init__(self, tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None,
                 run_path=None, input_path=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.run_path = Path(run_path).resolve()
        self.input_path = input_path

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            super().__call__(*args, **kwargs)
            r = subprocess.run(args=[sys.executable,
                                     str(self.run_path),
                                     str(Path(self.input_path).resolve())],
                               capture_output=True,
                               check=True)
            return r

        if self.episode is not None:
            return self.episode(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)
