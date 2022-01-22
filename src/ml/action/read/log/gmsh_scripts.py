from pathlib import Path

from src.ml.action.action import Action


class GmshScripts(Action):
    def __init__(self, tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None,
                 log_path=None, values=None, last=True):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.log_path = log_path
        self.values = [] if values is None else values
        self.last = last

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            super().__call__(*args, **kwargs)
            fs = {}  # features
            with open(Path(self.log_path).resolve()) as f:
                for line in f:
                    for v in self.values:
                        r = v(line=line)
                        if r is not None:
                            fs.setdefault(v.name, []).append(r)
            if self.last:
                fs = {k: v[-1] for k, v in fs.items()}
            return fs

        if self.episode is not None:
            return self.episode(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)
