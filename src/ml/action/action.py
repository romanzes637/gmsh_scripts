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

STATE = []


class Action:
    def __init__(self, tag=None, state_tag=None, subactions=None, executor=None,
                 propagate_state_tag=None):
        self.subactions = [] if subactions is None else subactions
        self.tag = tag if tag is not None else str(uuid.uuid4())
        self.state_tag = state_tag if state_tag is not None else str(uuid.uuid4())
        self.executor = executor  # 'thread' or 'process' or None (consecutive)
        self.propagate_state_tag = True if propagate_state_tag is None else False
        self.do_propagate_state_tag()

    def __call__(self, *args, **kwargs):
        if self.executor == 'thread':
            executor = concurrent.futures.ThreadPoolExecutor()
        elif self.executor == 'process':
            executor = concurrent.futures.ProcessPoolExecutor()
        else:  # consecutive
            executor = None
        if executor is not None:
            future_to_action = {executor.submit(x, *args, *kwargs): x
                                for x in self.subactions}
            for f in concurrent.futures.as_completed(future_to_action):
                a = future_to_action[f]
                try:
                    r = f.result()
                except Exception as e:
                    a.add_state(args, kwargs, None, [e])
                else:
                    a.add_state(args, kwargs, r, None)
            executor.shutdown()
        else:
            for a in self.subactions:
                try:
                    r = a(args, kwargs)
                except Exception as e:
                    a.add_state(args, kwargs, None, [e])
                else:
                    a.add_state(args, kwargs, r, None)
        return None

    def add_state(self, args, kwargs, result, exceptions):
        state = self.get_state()
        s = {'action': {'tag': self.tag,
                        'state_tag': self.state_tag,
                        'subactions_tags': [x.tag for x in self.subactions],
                        'subactions_state_tags': [x.state_tag for x in self.subactions],
                        'executor': self.executor},
             'args': args,
             'kwargs': kwargs,
             'result': result,
             'exceptions': exceptions}
        state.append(s)

    def get_state(self):
        assert self.state_tag is not None
        global STATE
        return STATE

    def do_propagate_state_tag(self):
        for x in self.subactions:
            x.state_tag = self.state_tag
            x.do_propagate_state_tag()
