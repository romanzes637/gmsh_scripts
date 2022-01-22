"""Base class for all actions (processes)

0. Python concurrency https://docs.python.org/3/library/concurrency.html
2. shared memory
    2.1 multithreading (by global variables, thanks to GIL) Now
    2.2 redis (memcached, relational DB)
    2.3 multiprocessing https://docs.python.org/3/library/multiprocessing.shared_memory.html
    2.4 Ray? Spark? Dask? https://github.com/ray-project/ray https://blog.dominodatalab.com/spark-dask-ray-choosing-the-right-framework
4. optuna integration
5. mouse integration

"""
import concurrent.futures
import uuid


class Action:
    def __init__(self, tag=None, subactions=None, executor=None,
                 state=None, do_propagate_state=None):
        self.subactions = [] if subactions is None else subactions
        self.tag = tag if tag is not None else str(uuid.uuid4())
        self.executor = executor  # 'thread' or 'process' or None (consecutive)
        self.state = state
        self.do_propagate_state = True if do_propagate_state is None else False
        self.propagate_state()

    def propagate_state(self):
        for x in self.subactions:
            x.state = self.state
            x.propagate_state()

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            if self.executor == 'thread':
                executor = concurrent.futures.ThreadPoolExecutor()
            elif self.executor == 'process':
                executor = concurrent.futures.ProcessPoolExecutor()
            else:  # consecutive
                executor = None
            if executor is not None:
                for future in concurrent.futures.as_completed(executor.submit(
                        a, *args, *kwargs) for a in self.subactions):
                    future.result()
                executor.shutdown()
            else:
                for a in self.subactions:
                    a(*args, **kwargs)
            return None

        if self.state is not None:
            return self.state(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)
