import time
import datetime
import socket
import os
import getpass
import uuid

EPISODE = []


class Episode:
    def __init__(self, tag=None, *args, **kwargs):
        self.tag = tag if tag is not None else str(uuid.uuid4())

    def __call__(self, f, *args, **kwargs):
        def wrapper(*args, **kwargs):
            a = args[0]  # Action instance
            meta = {}
            meta['timestamp'] = datetime.datetime.now().astimezone().isoformat()
            meta['hostname'] = socket.gethostname()
            meta['ip'] = socket.gethostbyname(socket.gethostname())
            meta['user'] = getpass.getuser()
            meta['pid'] = os.getpid()
            t0 = time.perf_counter()
            try:
                r = f(*args, **kwargs)
            except Exception as e:
                r = None
                meta['error'] = str(e)
            meta['dt'] = time.perf_counter() - t0
            self.add_state(a, f, args[1:], kwargs, r, meta)
            return r

        return wrapper

    def add_state(self, a, f, args, kwargs, result, meta):
        state = self.get_state()
        s = {'action': {'tag': a.tag,
                        'type': a.__module__ + '.' + a.__class__.__qualname__,
                        'function': f.__module__ + '.' + f.__qualname__,
                        'state_tag': a.episode.tag,
                        'subactions_tags': [x.tag for x in a.subactions],
                        'subactions_state_tags': [x.episode.tag for x in a.subactions],
                        'executor': a.executor},
             'args': args,
             'kwargs': kwargs,
             'result': result,
             'meta': meta}
        state.append(s)

    def get_state(self):
        assert self.tag is not None
        global EPISODE
        return EPISODE
