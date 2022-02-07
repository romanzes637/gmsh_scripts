import sys
from pathlib import Path

from src.ml.action.run.subprocess import Subprocess


class GmshScripts(Subprocess):
    def __init__(self, run_path=None, input_path=None, output_path=None,
                 output_formats=None, log_path=None, log_level=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.run_path = Path(run_path).resolve()
        self.input_path = input_path
        self.output_path = output_path
        self.output_formats = output_formats
        self.log_path = log_path
        self.log_level = log_level

    def post_call(self, stack_trace=None, *args, **kwargs):
        a = [sys.executable,
             str(self.run_path),
             str(Path(self.input_path).resolve())]
        if self.output_path is not None:
            a.append('-o')
            a.append(str(Path(self.output_path).resolve()))
        if self.output_formats is not None:
            a.append('-f')
            a.extend(self.output_formats)
        if self.log_path is not None:
            a.append('-l')
            a.append(str(Path(self.log_path).resolve()))
        if self.log_level is not None:
            a.append('-v')
            a.append(self.log_level)
        self.subprocess_kwargs['args'] = a
        super().post_call(stack_trace=stack_trace, *args, **kwargs)
