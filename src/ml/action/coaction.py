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
    def __init__(self, executor=None, executor_kwargs=None,
                 sub_executor=None, sub_executor_kwargs=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.executor = executor
        self.executor_kwargs = {} if executor_kwargs is None else executor_kwargs
        self.sub_executor = sub_executor
        self.sub_executor_kwargs = {} if sub_executor_kwargs is None else sub_executor_kwargs

    def sub_call(self, stack_trace=None, *args, **kwargs):
        if self.sub_executor is None:
            super().sub_call(stack_trace=stack_trace, *args, **kwargs)
        else:
            n = 0  # sub actions done
            executor = getattr(concurrent.futures, self.sub_executor)
            with executor(**self.sub_executor_kwargs) as e:
                if self.sub_jobs is None and self.sub_timeout is None:
                    if self.sub_routine == 'scatter':
                        while True:
                            fs = (e.submit(x, stack_trace=stack_trace, *args, **kwargs)
                                  for x in self.sub_actions)
                            for f in concurrent.futures.as_completed(fs=fs):
                                f.result()
                            n += len(self.sub_actions)
                    else:  # 'broadcast
                        w = e._max_workers
                        i = 0
                        while True:
                            if len(self.sub_actions) == 0:
                                continue
                            elif len(self.sub_actions) == i:
                                i = 0
                            else:
                                i += 1
                            a = self.sub_actions[i]
                            fs = (e.submit(a, stack_trace=stack_trace, *args, **kwargs)
                                  for _ in range(w))
                            for f in concurrent.futures.as_completed(fs=fs):
                                f.result()
                            n += w
                elif self.sub_jobs is None and self.sub_timeout is not None:
                    if self.sub_routine == 'scatter':
                        t = time.time()
                        while time.time() - t < self.sub_timeout:
                            fs = (e.submit(x, stack_trace=stack_trace, *args, **kwargs)
                                  for x in self.sub_actions)
                            try:
                                for f in concurrent.futures.as_completed(
                                        fs=fs, timeout=self.sub_timeout - (time.time() - t)):
                                    f.result()
                                n += len(self.sub_actions)
                            except concurrent.futures.TimeoutError as te:
                                u = int(str(te).split('(')[0].strip()) - 1  # undone -1 because wait=True for with ...
                                n += len(self.sub_actions) - u
                    else:  # 'broadcast
                        t = time.time()
                        w = e._max_workers
                        i = 0
                        while time.time() - t < self.sub_timeout:
                            if len(self.sub_actions) == 0:
                                continue
                            elif len(self.sub_actions) == i:
                                i = 0
                            else:
                                i += 1
                            a = self.sub_actions[i]
                            fs = (e.submit(a, stack_trace=stack_trace, *args, **kwargs)
                                  for _ in range(w))
                            try:
                                for f in concurrent.futures.as_completed(
                                        fs=fs, timeout=self.sub_timeout - (time.time() - t)):
                                    f.result()
                                n += w
                            except concurrent.futures.TimeoutError as te:
                                u = int(str(te).split('(')[0].strip()) - 1  # undone -1 because wait=True for with ...
                                n += w - u
                else:  # self.sub_jobs is not None
                    if self.sub_routine == 'scatter':
                        fs = (e.submit(x, stack_trace=stack_trace, *args, **kwargs)
                              for _ in range(self.sub_jobs) for x in self.sub_actions)
                    else:  # 'broadcast'
                        fs = (e.submit(x, stack_trace=stack_trace, *args, **kwargs)
                              for x in self.sub_actions for _ in range(self.sub_jobs))
                    try:
                        for f in concurrent.futures.as_completed(
                                fs=fs, timeout=self.sub_timeout):
                            f.result()
                        n += len(self.sub_actions) * self.sub_jobs
                    except concurrent.futures.TimeoutError as te:
                        u = int(str(te).split('(')[0].strip()) - 1  # undone -1 because wait=True for with ...
                        n += len(self.sub_actions) * self.sub_jobs - u

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
        if self.executor is None:
            super().__call__(stack_trace=stack_trace, *args, **kwargs)
        else:
            stack_trace = [self] if stack_trace is None else stack_trace + [self]
            n = 0  # jobs done
            executor = getattr(concurrent.futures, self.executor)
            with executor(**self.executor_kwargs) as e:
                if self.jobs is None and self.timeout is None:
                    w = e._max_workers
                    while True:
                        fs = (e.submit(self.call, stack_trace=stack_trace, *args, **kwargs)
                              for _ in range(w))
                        try:
                            for f in concurrent.futures.as_completed(fs=fs):
                                f.result()
                            n += w
                        except Exception as e:
                            pass
                elif self.jobs is None and self.timeout is not None:
                    t = time.time()
                    w = e._max_workers
                    while time.time() - t < self.timeout:
                        fs = (e.submit(self.call, stack_trace=stack_trace, *args, **kwargs)
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
                    fs = (e.submit(self.call, stack_trace=stack_trace, *args, **kwargs)
                          for _ in range(self.jobs))
                    try:
                        for f in concurrent.futures.as_completed(
                                fs=fs, timeout=self.timeout):
                            f.result()
                        n += self.jobs
                    except concurrent.futures.TimeoutError as te:
                        u = int(str(te).split('(')[0].strip()) - 1  # undone -1 because wait=True for with ...
                        n += self.jobs - u
            for cb in self.callbacks:
                cb(stack_trace=stack_trace, *args, **kwargs)
