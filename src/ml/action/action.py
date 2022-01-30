"""Base class for all actions (processes)

-1. TODO Track proposal 3148! https://www.python.org/dev/peps/pep-3148/
0. Python concurrency https://docs.python.org/3/library/concurrency.html
2. Shared memory
    2.1 multithreading (by global variables, thanks to GIL) Now
    2.2 redis (memcached, relational DB)
    2.3 multiprocessing https://docs.python.org/3/library/multiprocessing.shared_memory.html
    2.4 Ray? Spark? Dask? https://github.com/ray-project/ray https://blog.dominodatalab.com/spark-dask-ray-choosing-the-right-framework
4. Optuna integration
5. Mouse integration

"""
import concurrent.futures
import logging
import uuid
import time


class Action:
    def __init__(self, tag=None, sub_actions=None,
                 executor=None, executor_kwargs=None, sub_timeout=None,
                 pre_callbacks=None, pre_sub_callbacks=None, sub_post_callbacks=None, post_callbacks=None):
        self.tag = str(uuid.uuid4()) if tag is None else tag
        self.sub_actions = [] if sub_actions is None else sub_actions
        self.executor = executor
        self.executor_kwargs = {} if executor_kwargs is None else executor_kwargs
        self.sub_timeout = sub_timeout
        self.pre_callbacks = [] if pre_callbacks is None else pre_callbacks
        self.pre_sub_callbacks = [] if pre_sub_callbacks is None else pre_sub_callbacks
        self.sub_post_callbacks = [] if sub_post_callbacks is None else sub_post_callbacks
        self.post_callbacks = [] if post_callbacks is None else post_callbacks

    def pre_call(self, action=None, *args, **kwargs):
        return self, action

    def sub_call(self, action=None, *args, **kwargs):
        if self.executor is None:
            if self.sub_timeout is None:
                for a in self.sub_actions:
                    a(action=self, *args, **kwargs)
            else:
                t = time.time()
                for i, a in enumerate(self.sub_actions):
                    if time.time() - t > self.sub_timeout:
                        n = len(self.sub_actions)
                        logging.warning(f'{n - i}/{n} subactions unfinished')
                    a(action=self, *args, **kwargs)
        else:
            executor = getattr(concurrent.futures, self.executor)
            try:
                with executor(**self.executor_kwargs) as e:
                    fs = (e.submit(a, action=self, *args, **kwargs) for a in self.sub_actions)
                    for f in concurrent.futures.as_completed(fs=fs, timeout=self.sub_timeout):
                        f.result()
            except concurrent.futures.TimeoutError as timeout_error:
                logging.warning(timeout_error)
        return self, action

    def post_call(self, action=None, *args, **kwargs):
        return self, action

    def pre_callback(self, action=None, *args, **kwargs):
        for cb in self.pre_callbacks:
            cb(action=action, *args, **kwargs)
        return self, action

    def pre_sub_callback(self, action=None, *args, **kwargs):
        for cb in self.pre_sub_callbacks:
            cb(action=action, *args, **kwargs)
        return self, action

    def sub_post_callback(self, action=None, *args, **kwargs):
        for cb in self.sub_post_callbacks:
            cb(action=action, *args, **kwargs)
        return self, action

    def post_callback(self, action=None, *args, **kwargs):
        for cb in self.post_callbacks:
            cb(action=action, *args, **kwargs)
        return self, action

    def __call__(self, action=None, *args, **kwargs):
        self.pre_callback(action=action, *args, **kwargs)
        self.pre_call(action=action, *args, **kwargs)
        self.pre_sub_callback(action=action, *args, **kwargs)
        self.sub_call(action=action, *args, **kwargs)
        self.sub_post_callback(action=action, *args, **kwargs)
        self.post_call(action=action, *args, **kwargs)
        self.post_callback(action=action, *args, **kwargs)
        return self, action
