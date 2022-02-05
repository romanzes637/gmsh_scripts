"""Base class for all concurrent actions (processes)

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
import time
import os

from src.ml.action.action import Action


class Coaction(Action):
    def __init__(self,
                 jobs=1, timeout=None, routine=None,
                 executor=None, executor_kwargs=None,
                 sub_jobs=1, sub_timeout=None, sub_routine=None,
                 sub_executor=None, sub_executor_kwargs=None,
                 pre_cb_jobs=1, pre_cb_timeout=None, pre_cb_routine=None,
                 pre_cb_executor=None, pre_cb_executor_kwargs=None,
                 cb_jobs=1, cb_timeout=None, cb_routine=None,
                 cb_executor=None, cb_executor_kwargs=None,
                 pre_pre_cb_jobs=1, pre_pre_cb_timeout=None, pre_pre_cb_routine=None,
                 pre_pre_cb_executor=None, pre_pre_cb_executor_kwargs=None,
                 pre_sub_cb_jobs=1, pre_sub_cb_timeout=None, pre_sub_cb_routine=None,
                 pre_sub_cb_executor=None, pre_sub_cb_executor_kwargs=None,
                 sub_post_cb_jobs=1, sub_post_cb_timeout=None, sub_post_cb_routine=None,
                 sub_post_cb_executor=None, sub_post_cb_executor_kwargs=None,
                 post_cb_jobs=1, post_cb_timeout=None, post_cb_routine=None,
                 post_cb_executor=None, post_cb_executor_kwargs=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.jobs = jobs
        self.timeout = timeout
        self.routine = 'scatter' if routine is None else routine
        self.executor = executor
        self.executor_kwargs = {} if executor_kwargs is None else executor_kwargs
        self.sub_jobs = sub_jobs
        self.sub_timeout = sub_timeout
        self.sub_routine = 'scatter' if sub_routine is None else sub_routine
        self.sub_executor = sub_executor
        self.sub_executor_kwargs = {} if sub_executor_kwargs is None else sub_executor_kwargs
        self.pre_cb_jobs = pre_cb_jobs
        self.pre_cb_timeout = pre_cb_timeout
        self.pre_cb_routine = 'broadcast' if pre_cb_routine is None else pre_cb_routine
        self.pre_cb_executor = pre_cb_executor
        self.pre_cb_executor_kwargs = {} if pre_cb_executor_kwargs is None else pre_cb_executor_kwargs
        self.cb_jobs = cb_jobs
        self.cb_timeout = cb_timeout
        self.cb_routine = 'broadcast' if cb_routine is None else cb_routine
        self.cb_executor = cb_executor
        self.cb_executor_kwargs = {} if cb_executor_kwargs is None else cb_executor_kwargs
        self.pre_pre_cb_jobs = pre_pre_cb_jobs
        self.pre_pre_cb_timeout = pre_pre_cb_timeout
        self.pre_pre_cb_routine = 'broadcast' if pre_pre_cb_routine is None else pre_pre_cb_routine
        self.pre_pre_cb_executor = pre_pre_cb_executor
        self.pre_pre_cb_executor_kwargs = {} if pre_pre_cb_executor_kwargs is None else pre_pre_cb_executor_kwargs
        self.pre_sub_cb_jobs = pre_sub_cb_jobs
        self.pre_sub_cb_timeout = pre_sub_cb_timeout
        self.pre_sub_cb_routine = 'broadcast' if pre_sub_cb_routine is None else pre_sub_cb_routine
        self.pre_sub_cb_executor = pre_sub_cb_executor
        self.pre_sub_cb_executor_kwargs = {} if pre_sub_cb_executor_kwargs is None else pre_sub_cb_executor_kwargs
        self.sub_post_cb_jobs = sub_post_cb_jobs
        self.sub_post_cb_timeout = sub_post_cb_timeout
        self.sub_post_cb_routine = 'broadcast' if sub_post_cb_routine is None else sub_post_cb_routine
        self.sub_post_cb_executor = sub_post_cb_executor
        self.sub_post_cb_executor_kwargs = {} if sub_post_cb_executor_kwargs is None else sub_post_cb_executor_kwargs
        self.post_cb_jobs = post_cb_jobs
        self.post_cb_timeout = post_cb_timeout
        self.post_cb_routine = 'broadcast' if post_cb_routine is None else post_cb_routine
        self.post_cb_executor = post_cb_executor
        self.post_cb_executor_kwargs = {} if post_cb_executor_kwargs is None else post_cb_executor_kwargs

    @staticmethod
    def co_call(calls, stack_trace=None, jobs=1, timeout=None, routine='scatter',
                executor=None, executor_kwargs=None, *args, **kwargs):
        if executor is None:  # Sequential
            if jobs is None and timeout is None:
                while True:
                    for c in calls:
                        c(stack_trace=stack_trace, *args, **kwargs)
            elif jobs is not None and timeout is None:
                if routine == 'scatter':
                    for _ in range(jobs):
                        for c in calls:
                            c(stack_trace=stack_trace, *args, **kwargs)
                else:  # 'broadcast'
                    for c in calls:
                        for _ in range(jobs):
                            c(stack_trace=stack_trace, *args, **kwargs)
            elif jobs is None and timeout is not None:
                t = time.time()
                while time.time() - t < timeout:
                    for c in calls:
                        c(stack_trace=stack_trace, *args, **kwargs)
            else:  # self.jobs is not None and self.timeout is not None
                t = time.time()
                if routine == 'scatter':
                    for _ in range(jobs):
                        for c in calls:
                            if time.time() - t >= timeout:
                                break
                            c(stack_trace=stack_trace, *args, **kwargs)
                else:  # 'broadcast'
                    for c in calls:
                        for _ in range(jobs):
                            if time.time() - t >= timeout:
                                break
                            c(stack_trace=stack_trace, *args, **kwargs)
        else:  # Concurrent
            n = 0  # actions done
            executor = getattr(concurrent.futures, executor)
            with executor(**executor_kwargs) as e:
                if jobs is None and timeout is None:
                    if routine == 'scatter':
                        while True:
                            fs = (e.submit(x, stack_trace=stack_trace, *args, **kwargs)
                                  for x in calls)
                            for f in concurrent.futures.as_completed(fs=fs):
                                f.result()
                            n += len(calls)
                    else:  # 'broadcast
                        w = e._max_workers
                        i = 0
                        while True:
                            if len(calls) == 0:
                                continue
                            elif len(calls) == i:
                                i = 0
                            else:
                                i += 1
                            c = calls[i]
                            fs = (e.submit(c, stack_trace=stack_trace, *args, **kwargs)
                                  for _ in range(w))
                            for f in concurrent.futures.as_completed(fs=fs):
                                f.result()
                            n += w
                elif jobs is None and timeout is not None:
                    if routine == 'scatter':
                        t = time.time()
                        while time.time() - t < timeout:
                            fs = (e.submit(x, stack_trace=stack_trace, *args, **kwargs)
                                  for x in calls)
                            try:
                                for f in concurrent.futures.as_completed(
                                        fs=fs, timeout=timeout - (time.time() - t)):
                                    f.result()
                                n += len(calls)
                            except concurrent.futures.TimeoutError as te:
                                u = int(str(te).split('(')[0].strip()) - 1  # undone -1 because wait=True for with ...
                                n += len(calls) - u
                    else:  # 'broadcast
                        t = time.time()
                        w = e._max_workers
                        i = 0
                        while time.time() - t < timeout:
                            if len(calls) == 0:
                                continue
                            elif len(calls) == i:
                                i = 0
                            else:
                                i += 1
                            c = calls[i]
                            fs = (e.submit(c, stack_trace=stack_trace, *args, **kwargs)
                                  for _ in range(w))
                            try:
                                for f in concurrent.futures.as_completed(
                                        fs=fs, timeout=timeout - (time.time() - t)):
                                    f.result()
                                n += w
                            except concurrent.futures.TimeoutError as te:
                                u = int(str(te).split('(')[0].strip()) - 1  # undone -1 because wait=True for with ...
                                n += w - u
                else:  # self.sub_jobs is not None
                    if routine == 'scatter':
                        fs = (e.submit(x, stack_trace=stack_trace, *args, **kwargs)
                              for _ in range(jobs) for x in calls)
                    else:  # 'broadcast'
                        fs = (e.submit(x, stack_trace=stack_trace, *args, **kwargs)
                              for x in calls for _ in range(jobs))
                    try:
                        for f in concurrent.futures.as_completed(
                                fs=fs, timeout=timeout):
                            f.result()
                        n += len(calls) * jobs
                    except concurrent.futures.TimeoutError as te:
                        u = int(str(te).split('(')[0].strip()) - 1  # undone -1 because wait=True for with ...
                        n += len(calls) * jobs - u

    def pre_pre_callback(self, stack_trace=None, *args, **kwargs):
        self.co_call(
            calls=self.pre_pre_callbacks, stack_trace=stack_trace,
            jobs=self.pre_pre_cb_jobs, timeout=self.pre_pre_cb_timeout,
            routine=self.pre_pre_cb_routine,
            executor=self.pre_pre_cb_executor,
            executor_kwargs=self.pre_pre_cb_executor_kwargs,
            *args, **kwargs)

    def pre_sub_callback(self, stack_trace=None, *args, **kwargs):
        self.co_call(
            calls=self.pre_sub_callbacks, stack_trace=stack_trace,
            jobs=self.pre_sub_cb_jobs, timeout=self.pre_sub_cb_timeout,
            routine=self.pre_sub_cb_routine,
            executor=self.pre_sub_cb_executor,
            executor_kwargs=self.pre_sub_cb_executor_kwargs,
            *args, **kwargs)

    def sub_call(self, stack_trace=None, *args, **kwargs):
        self.co_call(
            calls=self.sub_actions, stack_trace=stack_trace,
            jobs=self.jobs, timeout=self.timeout, routine=self.routine,
            executor=self.executor, executor_kwargs=self.executor_kwargs,
            *args, **kwargs)

    def sub_post_callback(self, stack_trace=None, *args, **kwargs):
        self.co_call(
            calls=self.sub_post_callbacks, stack_trace=stack_trace,
            jobs=self.sub_post_cb_jobs, timeout=self.sub_post_cb_timeout,
            routine=self.sub_post_cb_routine,
            executor=self.sub_post_cb_executor,
            executor_kwargs=self.sub_post_cb_executor_kwargs,
            *args, **kwargs)

    def post_callback(self, stack_trace=None, *args, **kwargs):
        self.co_call(
            calls=self.post_callbacks, stack_trace=stack_trace,
            jobs=self.post_cb_jobs, timeout=self.post_cb_timeout,
            routine=self.post_cb_routine,
            executor=self.post_cb_executor,
            executor_kwargs=self.post_cb_executor_kwargs,
            *args, **kwargs)

    def pre_callback(self, stack_trace=None, *args, **kwargs):
        self.co_call(
            calls=self.pre_callbacks, stack_trace=stack_trace,
            jobs=self.pre_cb_jobs, timeout=self.pre_cb_timeout, routine=self.pre_cb_routine,
            executor=self.pre_cb_executor, executor_kwargs=self.pre_cb_executor_kwargs,
            *args, **kwargs)

    def call(self, stack_trace=None, *args, **kwargs):
        calls = [self.pre_pre_callback, self.pre_call, self.pre_sub_callback,
                 self.sub_call, self.sub_post_callback, self.post_call,
                 self.post_callback]
        self.co_call(
            calls=calls, stack_trace=stack_trace,
            jobs=self.jobs, timeout=self.timeout, routine=self.routine,
            executor=self.executor, executor_kwargs=self.executor_kwargs,
            *args, **kwargs)

    def callback(self, stack_trace=None, *args, **kwargs):
        self.co_call(
            calls=self.callbacks, stack_trace=stack_trace,
            jobs=self.cb_jobs, timeout=self.cb_timeout, routine=self.cb_routine,
            executor=self.cb_executor, executor_kwargs=self.cb_executor_kwargs,
            *args, **kwargs)

    def __call__(self, stack_trace=None, *args, **kwargs):
        st = [self] if stack_trace is None else stack_trace + [self]
        print(f'{os.getpid()} {" <- ".join([x.uid if x.tag is None else x.tag for x in st[::-1]])}, '
              f'{self.executor if self.executor is not None else "SequenceExecutor"}/'
              f'{self.sub_executor if self.sub_executor is not None else "SequenceExecutor"}, '
              f'{self.executor_kwargs.get("max_workers", "max")}/'
              f'{self.sub_executor_kwargs.get("max_workers", "max")} worker(s), '
              f'{self.jobs if self.jobs is not None else "inf"}/'
              f'{self.sub_jobs if self.jobs is not None else "inf"} job(s), '
              f'{self.timeout if self.timeout is not None else "inf"}/'
              f'{self.sub_timeout if self.sub_timeout is not None else "inf"} timeout, '
              f'{type(self)}')
        super().__call__(stack_trace=stack_trace, *args, **kwargs)
