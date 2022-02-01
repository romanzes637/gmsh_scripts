"""Base class for all actions (processes)

1. TODO implement stack_trace using traceback or trace modules?
2. TODO implement stack_trace using uid only as key in the database? Redis?
"""
import uuid
import time


class Action:
    def __init__(self, tag=None, sub_actions=None, sup_action=None,
                 jobs=1, timeout=None, sub_jobs=1, sub_timeout=None,
                 pre_call=None, sub_call=None, post_call=None, call=None,
                 pre_callbacks=None, pre_sub_callbacks=None,
                 sub_post_callbacks=None, post_callbacks=None, callbacks=None):
        self.uid = str(uuid.uuid4())
        self.tag = tag
        self.sub_actions = [] if sub_actions is None else sub_actions
        self.sup_action = sup_action
        for a in self.sub_actions:
            a.sup_action = self
        self.jobs = jobs
        self.timeout = timeout
        self.sub_jobs = sub_jobs
        self.sub_timeout = sub_timeout
        if pre_call is not None:
            self.pre_call = pre_call
        if sub_call is not None:
            self.sub_call = sub_call
        if post_call is not None:
            self.post_call = post_call
        if call is not None:
            self.call = call
        self.pre_callbacks = [] if pre_callbacks is None else pre_callbacks
        self.pre_sub_callbacks = [] if pre_sub_callbacks is None else pre_sub_callbacks
        self.sub_post_callbacks = [] if sub_post_callbacks is None else sub_post_callbacks
        self.post_callbacks = [] if post_callbacks is None else post_callbacks
        self.callbacks = [] if callbacks is None else callbacks

    def pre_call(self, stack_trace=None, *args, **kwargs):
        pass

    def sub_call(self, stack_trace=None, *args, **kwargs):
        if self.jobs is None and self.timeout is None:
            while True:
                for a in self.sub_actions:
                    a(stack_trace=stack_trace)
        elif self.jobs is not None and self.timeout is None:
            for _ in range(self.sub_jobs):
                for a in self.sub_actions:
                    a(stack_trace=stack_trace)
        elif self.jobs is None and self.timeout is not None:
            t = time.time()
            while time.time() - t < self.timeout:
                for a in self.sub_actions:
                    a(stack_trace=stack_trace)
        else:  # self.jobs is not None and self.timeout is not None
            t = time.time()
            for _ in range(self.jobs):
                if time.time() - t >= self.timeout:
                    break
                for a in self.sub_actions:
                    a(stack_trace=stack_trace)

    def post_call(self, stack_trace=None, *args, **kwargs):
        pass

    def call(self, stack_trace=None, *args, **kwargs):
        for cb in self.pre_callbacks:
            cb(stack_trace=stack_trace, *args, **kwargs)
        self.pre_call(stack_trace=stack_trace, *args, **kwargs)
        for cb in self.pre_sub_callbacks:
            cb(stack_trace=stack_trace, *args, **kwargs)
        self.sub_call(stack_trace=stack_trace, *args, **kwargs)
        for cb in self.sub_post_callbacks:
            cb(stack_trace=stack_trace, *args, **kwargs)
        self.post_call(stack_trace=stack_trace, *args, **kwargs)
        for cb in self.post_callbacks:
            cb(stack_trace=stack_trace, *args, **kwargs)

    def __call__(self, stack_trace=None, *args, **kwargs):
        stack_trace = [self] if stack_trace is None else stack_trace + [self]
        if self.jobs is None and self.timeout is None:
            while True:
                self.call(stack_trace=stack_trace, *args, **kwargs)
        elif self.jobs is not None and self.timeout is None:
            for _ in range(self.jobs):
                self.call(stack_trace=stack_trace, *args, **kwargs)
        elif self.jobs is None and self.timeout is not None:
            t = time.time()
            while time.time() - t < self.timeout:
                self.call(stack_trace=stack_trace, *args, **kwargs)
        else:  # self.jobs is not None and self.timeout is not None
            t = time.time()
            for _ in range(self.jobs):
                if time.time() - t >= self.timeout:
                    break
                self.call(stack_trace=stack_trace, *args, **kwargs)
        for cb in self.callbacks:
            cb(stack_trace=stack_trace, *args, **kwargs)
