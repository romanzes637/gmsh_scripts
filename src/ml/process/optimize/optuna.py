from src.ml.process.process import Process


class Optuna(Process):
    def __init__(self, processes=None):
        super().__init__()
        self.processes = [] if processes is None else processes

    def __call__(self, *args, **kwargs):
        for p in self.processes:
            p()
