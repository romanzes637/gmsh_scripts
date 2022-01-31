"""Base class for all actions (processes)

0. TODO Track proposal 3148! https://www.python.org/dev/peps/pep-3148/
1. About python concurrency https://docs.python.org/3/library/concurrency.html
2. TODO Shared memory
    2.1 multithreading (but GIL)
    2.2 multiprocessing https://docs.python.org/3/library/multiprocessing.shared_memory.html
    2.3 redis (memcached, relational DB)
    2.4 Ray? Spark? Dask? https://github.com/ray-project/ray https://blog.dominodatalab.com/spark-dask-ray-choosing-the-right-framework
3. TODO multiprocessing logging
    3.1 https://stackoverflow.com/questions/43949259/processpoolexecutor-logging-failed
    3.2 https://stackoverflow.com/questions/49782749/processpoolexecutor-logging-fails-to-log-inside-function-on-windows-but-not-on-u
4. TODO Handle signals (SIGTERM and SIGINT, etc)
"""
import concurrent.futures
import logging
import uuid
import time
import os


class Action:
    def __init__(self, tag=None, sub_actions=None, sup_action=None,
                 executor=None, executor_kwargs=None, jobs=1, timeout=None,
                 pre_call=None, sub_call=None, post_call=None, call=None,
                 pre_callbacks=None, pre_sub_callbacks=None,
                 sub_post_callbacks=None, post_callbacks=None, callbacks=None):
        self.uid = str(uuid.uuid4())
        self.tag = tag
        self.sub_actions = [] if sub_actions is None else sub_actions
        self.sup_action = sup_action
        for a in self.sub_actions:
            a.sup_action = self
        self.executor = executor
        self.executor_kwargs = {} if executor_kwargs is None else executor_kwargs
        self.jobs = jobs
        self.timeout = timeout
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

    def pre_call(self, actions=None, *args, **kwargs):
        pass

    def sub_call(self, actions=None, *args, **kwargs):
        for a in self.sub_actions:
            a(actions=actions)

    def post_call(self, actions=None, *args, **kwargs):
        pass

    def call(self, actions=None, *args, **kwargs):
        # print(f'{os.getpid()} {" <- ".join([x.tag for x in actions[::-1]])}, '
        #       f'{actions[-1].executor if actions[-1].executor is not None else "SequenceExecutor"}, '
        #       f'{actions[-1].executor_kwargs.get("max_workers", "max")} worker(s), '
        #       f'{actions[-1].jobs if actions[-1].jobs is not None else "inf"} job(s), '
        #       f'{actions[-1].timeout if actions[-1].timeout is not None else "inf"} timeout, '
        #       f'{type(self)}')
        for cb in self.pre_callbacks:
            cb(actions=actions, *args, **kwargs)
        self.pre_call(actions=actions, *args, **kwargs)
        for cb in self.pre_sub_callbacks:
            cb(actions=actions, *args, **kwargs)
        self.sub_call(actions=actions, *args, **kwargs)
        for cb in self.sub_post_callbacks:
            cb(actions=actions, *args, **kwargs)
        self.post_call(actions=actions, *args, **kwargs)
        for cb in self.post_callbacks:
            cb(actions=actions, *args, **kwargs)

    def __call__(self, actions=None, *args, **kwargs):
        actions = [self] if actions is None else actions + [self]
        n = 0
        if self.executor is None:
            if self.jobs is None and self.timeout is None:
                while True:
                    self.call(actions=actions, *args, **kwargs)
                    n += 1
            elif self.jobs is not None and self.timeout is None:
                for _ in range(self.jobs):
                    self.call(actions=actions, *args, **kwargs)
                    n += 1
            elif self.jobs is None and self.timeout is not None:
                t = time.time()
                while time.time() - t < self.timeout:
                    self.call(actions=actions, *args, **kwargs)
                    n += 1
            else:  # self.jobs is not None and self.timeout is not None
                t = time.time()
                for _ in range(self.jobs):
                    if time.time() - t >= self.timeout:
                        break
                    self.call(actions=actions, *args, **kwargs)
                    n += 1
        else:
            executor = getattr(concurrent.futures, self.executor)
            with executor(**self.executor_kwargs) as e:
                if self.jobs is None:
                    t = time.time()
                    w = e._max_workers
                    while time.time() - t < self.timeout:
                        fs = (e.submit(self.call, actions=actions, *args, **kwargs)
                              for _ in range(w))
                        try:
                            for f in concurrent.futures.as_completed(
                                    fs=fs, timeout=self.timeout - (time.time() - t)):
                                f.result()
                            n += w
                        except concurrent.futures.TimeoutError as te:
                            u = int(str(te).split('(')[0].strip()) - 1  # undone -1 because wait=True for with ...
                            n += w - u
                else:  # self.jobs is not None
                    fs = (e.submit(self.call, actions=actions, *args, **kwargs)
                          for _ in range(self.jobs))
                    try:
                        for f in concurrent.futures.as_completed(
                                fs=fs, timeout=self.timeout):
                            f.result()
                        n += self.jobs
                    except concurrent.futures.TimeoutError as te:
                        u = int(str(te).split('(')[0].strip()) - 1  # undone -1 because wait=True for with ...
                        n += self.jobs - u
        # print(f'{os.getpid()} {" <- ".join([x.tag for x in actions[::-1]])}, '
        #       f'{actions[-1].executor if actions[-1].executor is not None else "SequenceExecutor"}, '
        #       f'Done {n}/{self.jobs} job(s) with timeout {self.timeout}')
        for cb in self.callbacks:
            cb(actions=actions, *args, **kwargs)
