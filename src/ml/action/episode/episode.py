"""

1. TODO Implement callback of action
2. TODO Store states in DB
"""

import datetime
import socket
import os
import getpass
import uuid

from src.ml.action.coaction import Coaction

EPISODE = []


class Episode(Coaction):
    def __init__(self, tag=None, **kwargs):
        super().__init__(**kwargs)
        self.tag = str(uuid.uuid4()) if tag is None else tag

    def post_call(self, stack_trace=None, *args, **kwargs):
        global EPISODE

        meta = {}
        meta['timestamp'] = datetime.datetime.now().astimezone().isoformat()
        meta['hostname'] = socket.gethostname()
        meta['ip'] = socket.gethostbyname(socket.gethostname())
        meta['user'] = getpass.getuser()
        meta['pid'] = os.getpid()
        state = {'action': {'tag': stack_trace[-2].tag,
                            'sub_actions_tags': [x. tag for x in stack_trace[-2].sub_actions]
                            },
                 'args': args,
                 'kwargs': kwargs,
                 'meta': meta}
        EPISODE.append(state)
