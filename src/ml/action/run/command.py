import subprocess

from src.ml.action.action import Action


class Command(Action):
    def __init__(self, tag=None, state_tag=None, subactions=None, executor=None,
                 propagate_state_tag=None,
                 args=None, shell=False, check=False, capture_output=False):
        super().__init__(tag=tag, state_tag=state_tag, subactions=subactions,
                         executor=executor, propagate_state_tag=propagate_state_tag)
        self.args = ['echo', 'hello world'] if args is None else args
        self.shell = shell
        self.check = check
        self.capture_output = capture_output

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            super().__call__(*args, **kwargs)
            r = subprocess.run(args=self.args, shell=self.shell, check=self.check,
                               capture_output=self.capture_output)
            return r.returncode

        if self.state is not None:
            return self.state(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)
