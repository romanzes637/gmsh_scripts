import subprocess
import sys

from src.ml.action.run.run import Run


class Subprocess(Run):
    def __init__(self, subprocess_kwargs=None, nohup=True, **kwargs):
        super().__init__(**kwargs)
        self.subprocess_kwargs = {} if subprocess_kwargs is None else subprocess_kwargs
        self.result = None
        self.nohup = nohup

    def post_call(self, stack_trace=None, *args, **kwargs):
        if self.nohup and sys.platform != 'win32':
            self.subprocess_kwargs['args'] = \
                ['nohup'] + self.subprocess_kwargs.get('args', [])
        self.result = subprocess.run(**self.subprocess_kwargs)
