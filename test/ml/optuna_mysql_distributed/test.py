import unittest
import subprocess
import sys
from pathlib import Path


class TestLayer(unittest.TestCase):

    def test_ml(self):
        print('test ml.py')
        python = sys.executable
        cwd = Path(__file__).parent.resolve()
        root = cwd.parent.parent.parent
        script = root / "ml.py"
        print(f'python: {python}\nscript: {script}')
        files = [x for x in cwd.glob('*.json') if not x.name.startswith('_')]
        for i, f in enumerate(files):
            print(f'{i + 1}/{len(files)} {f}')
            args = [python, str(script), str(f)]
            result = subprocess.run(args, cwd=cwd)
            result.check_returncode()


if __name__ == '__main__':
    unittest.main()
