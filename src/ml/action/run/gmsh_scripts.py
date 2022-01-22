import subprocess
import sys
from pathlib import Path

from src.ml.action.action import Action


class GmshScripts(Action):
    def __init__(self, tag=None,  subactions=None, executor=None,
                 state=None, do_propagate_state=None,
                 run_path=None, input_path=None):
        super().__init__(tag=tag,  subactions=subactions, executor=executor,
                         state=state, do_propagate_state=do_propagate_state)
        self.run_path = run_path
        self.input_path = input_path

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            super().__call__(*args, **kwargs)
            r = subprocess.run(args=[sys.executable,
                                     str(Path(self.run_path).resolve()),
                                     str(Path(self.input_path).resolve())],
                               capture_output=True,
                               check=True)
            return r

        if self.state is not None:
            return self.state(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)
