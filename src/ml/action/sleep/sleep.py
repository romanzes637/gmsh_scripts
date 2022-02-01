import time

from src.ml.action.coaction import Coaction


class Sleep(Coaction):
    def __init__(self, secs=None, **kwargs):
        super().__init__(**kwargs)
        self.secs = secs

    def pre_call(self, stack_trace=None, *args, **kwargs):
        if self.secs is not None:
            time.sleep(self.secs)
