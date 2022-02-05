"""Base class for all actions (processes)

1. TODO implement stack_trace using traceback or trace modules?
2. TODO implement stack_trace using uid only as key in the database? Redis?
"""
import uuid
import time


class Action:
    def __init__(self, tag=None, sub_actions=None, sup_action=None,
                 call=None, pre_call=None, sub_call=None, post_call=None,
                 pre_callback=None, callback=None,
                 pre_pre_callback=None, pre_sub_callback=None,
                 sub_post_callback=None, post_callback=None,
                 pre_callbacks=None, callbacks=None,
                 pre_pre_callbacks=None, pre_sub_callbacks=None,
                 sub_post_callbacks=None, post_callbacks=None):
        self.uid = str(uuid.uuid4())
        self.tag = tag
        self.sub_actions = [] if sub_actions is None else sub_actions
        self.sup_action = sup_action
        for a in self.sub_actions:
            a.sup_action = self
        if call is not None:
            self.call = call
        if pre_call is not None:
            self.pre_call = pre_call
        if sub_call is not None:
            self.sub_call = sub_call
        if post_call is not None:
            self.post_call = post_call
        if pre_callback is not None:
            self.pre_callback = pre_callback
        if callback is not None:
            self.callback = callback
        if pre_pre_callback is not None:
            self.pre_pre_callback = pre_pre_callback
        if pre_sub_callback is not None:
            self.pre_sub_callback = pre_sub_callback
        if sub_post_callback is not None:
            self.sub_post_callback = sub_post_callback
        if post_callback is not None:
            self.post_callback = post_callback
        self.pre_callbacks = [] if pre_callbacks is None else pre_callbacks
        self.callbacks = [] if callbacks is None else callbacks
        self.pre_pre_callbacks = [] if pre_pre_callbacks is None else pre_pre_callbacks
        self.pre_sub_callbacks = [] if pre_sub_callbacks is None else pre_sub_callbacks
        self.sub_post_callbacks = [] if sub_post_callbacks is None else sub_post_callbacks
        self.post_callbacks = [] if post_callbacks is None else post_callbacks

    def pre_pre_callback(self, stack_trace=None, *args, **kwargs):
        for c in self.pre_pre_callbacks:
            c(stack_trace=stack_trace, *args, **kwargs)

    def pre_call(self, stack_trace=None, *args, **kwargs):
        pass

    def pre_sub_callback(self, stack_trace=None, *args, **kwargs):
        for c in self.pre_sub_callbacks:
            c(stack_trace=stack_trace, *args, **kwargs)

    def sub_call(self, stack_trace=None, *args, **kwargs):
        for a in self.sub_actions:
            a(stack_trace=stack_trace, *args, **kwargs)

    def sub_post_callback(self, stack_trace=None, *args, **kwargs):
        for c in self.sub_post_callbacks:
            c(stack_trace=stack_trace, *args, **kwargs)

    def post_call(self, stack_trace=None, *args, **kwargs):
        pass

    def post_callback(self, stack_trace=None, *args, **kwargs):
        for c in self.post_callbacks:
            c(stack_trace=stack_trace, *args, **kwargs)

    def pre_callback(self, stack_trace=None, *args, **kwargs):
        for c in self.pre_callbacks:
            c(stack_trace=stack_trace, *args, **kwargs)

    def call(self, stack_trace=None, *args, **kwargs):
        self.pre_pre_callback(stack_trace=stack_trace, *args, **kwargs)
        self.pre_call(stack_trace=stack_trace, *args, **kwargs)
        self.pre_sub_callback(stack_trace=stack_trace, *args, **kwargs)
        self.sub_call(stack_trace=stack_trace, *args, **kwargs)
        self.sub_post_callback(stack_trace=stack_trace, *args, **kwargs)
        self.post_call(stack_trace=stack_trace, *args, **kwargs)
        self.post_callback(stack_trace=stack_trace, *args, **kwargs)

    def callback(self, stack_trace=None, *args, **kwargs):
        for c in self.callbacks:
            c(stack_trace=stack_trace, *args, **kwargs)

    def __call__(self, stack_trace=None, *args, **kwargs):
        stack_trace = [self] if stack_trace is None else stack_trace + [self]
        self.pre_callback(stack_trace=stack_trace, *args, **kwargs)
        self.call(stack_trace=stack_trace, *args, **kwargs)
        self.callback(stack_trace=stack_trace, *args, **kwargs)
