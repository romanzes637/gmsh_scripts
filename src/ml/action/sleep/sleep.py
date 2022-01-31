import time

from src.ml.action.action import Action


class Sleep(Action):
    def __init__(self, secs=None, **kwargs):
        super().__init__(**kwargs)
        self.secs = secs

    def pre_call(self, actions=None, *args, **kwargs):
        if self.secs is not None:
            time.sleep(self.secs)
