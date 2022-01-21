from src.ml.action.action import Action


class Optuna(Action):
    def __init__(self, tag=None, state_tag=None, subactions=None, executor=None,
                 propagate_state_tag=None):
        super().__init__(tag=tag, state_tag=state_tag, subactions=subactions,
                         executor=executor, propagate_state_tag=propagate_state_tag)

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        return None
