import subprocess
import sys
from pathlib import Path
import io
import copy

from src.ml.action.run.run import Run


class Subprocess(Run):
    def __init__(self, subprocess_kwargs=None, nohup=True,
                 resolve_paths=False, resolve_cwd=False,
                 stdout_kwargs=None, stderr_kwargs=None, **kwargs):
        super().__init__(**kwargs)
        self.subprocess_kwargs = {} if subprocess_kwargs is None else subprocess_kwargs
        self.result = None
        self.stdout_kwargs = {} if stdout_kwargs is None else stdout_kwargs
        self.stderr_kwargs = {} if stderr_kwargs is None else stderr_kwargs
        self.nohup = nohup
        self.stdout_kwargs.setdefault('mode', 'w')
        self.stderr_kwargs.setdefault('mode', 'w')
        self.resolve_paths = resolve_paths
        self.resolve_cwd = resolve_cwd
        if self.resolve_paths:
            for i, a in enumerate(self.subprocess_kwargs.get('args', [])):
                p = Path(a).resolve()
                if p.exists():
                    self.subprocess_kwargs['args'][i] = str(p)
        if self.resolve_cwd:
            cwd = self.subprocess_kwargs.get('cwd', None)
            if cwd is not None:
                p = Path(cwd).resolve()
                if p.exists():
                    self.subprocess_kwargs['cwd'] = str(cwd)

    def post_call(self, stack_trace=None, *args, **kwargs):
        subprocess_kwargs = copy.deepcopy(self.subprocess_kwargs)
        if self.nohup and sys.platform != 'win32':
            subprocess_kwargs['args'] = \
                ['nohup'] + subprocess_kwargs.get('args', [])
        stdout = subprocess_kwargs.get('stdout', None)
        if stdout is not None:
            if stdout in ['PIPE', 'STDOUT', 'DEVNULL']:
                stdout = getattr(subprocess, stdout)
            else:
                stdout = open(file=Path(stdout).resolve(), **self.stdout_kwargs)
            subprocess_kwargs['stdout'] = stdout
        stderr = subprocess_kwargs.get('stderr', None)
        if stderr is not None:
            if stderr in ['PIPE', 'STDOUT', 'DEVNULL']:
                stderr = getattr(subprocess, stderr)
            else:
                stderr = open(file=Path(stderr).resolve(), **self.stderr_kwargs)
            subprocess_kwargs['stderr'] = stderr
        self.result = subprocess.run(**subprocess_kwargs)
        if isinstance(stdout, io.IOBase) and not stdout.closed:
            stdout.close()
        if isinstance(stderr, io.IOBase) and not stderr.closed:
            stderr.close()
