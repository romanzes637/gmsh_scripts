from src.ml.action.action import Action


class Optuna(Action):
    def __init__(self, tag=None, subactions=None, executor=None,
                 state=None, do_propagate_state=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         state=state, do_propagate_state=do_propagate_state)

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            return None

        if self.state is not None:
            return self.state(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)
