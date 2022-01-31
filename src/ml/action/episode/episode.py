"""

1. TODO Implement callback of action
2. TODO Store states in DB
"""

import datetime
import socket
import os
import getpass
import uuid

from src.ml.action.action import Action

EPISODE = []


class Episode(Action):
    def __init__(self, tag=None, **kwargs):
        super().__init__(**kwargs)
        self.tag = str(uuid.uuid4()) if tag is None else tag

    def post_call(self, actions=None, *args, **kwargs):
        global EPISODE

        meta = {}
        meta['timestamp'] = datetime.datetime.now().astimezone().isoformat()
        meta['hostname'] = socket.gethostname()
        meta['ip'] = socket.gethostbyname(socket.gethostname())
        meta['user'] = getpass.getuser()
        meta['pid'] = os.getpid()
        state = {'action': {'tag': actions[-2].tag,
                            'sub_actions_tags': [x. tag for x in actions[-2].sub_actions]
                            },
                 'args': args,
                 'kwargs': kwargs,
                 'meta': meta}
        EPISODE.append(state)
