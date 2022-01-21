import subprocess
import sys
from pathlib import Path

from src.ml.action.action import Action


class GmshScripts(Action):
    def __init__(self, tag=None, state_tag=None, subactions=None, executor=None,
                 propagate_state_tag=None,
                 run_path=None, input_path=None):
        super().__init__(tag=tag, state_tag=state_tag, subactions=subactions,
                         executor=executor, propagate_state_tag=propagate_state_tag)
        self.run_path = run_path
        self.input_path = input_path

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        r = subprocess.run(args=[sys.executable,
                                 str(Path(self.run_path).resolve()),
                                 str(Path(self.input_path).resolve())],
                           capture_output=True,
                           check=True)
        return r
