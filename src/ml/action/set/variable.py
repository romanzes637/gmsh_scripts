from src.ml.action.set.set import Set


class Variable(Set):
    def __init__(self, tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)

    def __call__(self, feature, *args, **kwargs):
        return feature
