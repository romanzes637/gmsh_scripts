from src.ml.action.action import Action


class Run(Action):
    def __init__(self, tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        pass
