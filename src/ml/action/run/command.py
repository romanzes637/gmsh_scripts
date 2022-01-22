import subprocess

from src.ml.action.action import Action


class Command(Action):
    def __init__(self, tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None,
                 args=None, shell=False, check=False, capture_output=False):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
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

        if self.episode is not None:
            return self.episode(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)
