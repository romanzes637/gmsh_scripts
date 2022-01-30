import subprocess

from src.ml.action.action import Action


class Subprocess(Action):
    def __init__(self, subprocess_kwargs=None, **kwargs):
        super().__init__(**kwargs)
        self.subprocess_kwargs = {} if subprocess_kwargs is None else subprocess_kwargs
        self.returncode = 0

    def post_call(self, action=None, *args, **kwargs):
        r = subprocess.run(**self.subprocess_kwargs)
        self.returncode = r.returncode
        return self, action


