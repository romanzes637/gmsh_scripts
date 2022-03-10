import unittest
import subprocess
import sys
from pathlib import Path


class TestGmsh(unittest.TestCase):

    def test_opt(self):
        python = sys.executable
        cwd = Path(__file__).parent.resolve()
        root = cwd.parent.parent.parent
        script = root / "ml.py"
        args = [python, str(script), 'opt.json']
        result = subprocess.run(args, cwd=cwd)
        print(result.returncode)
        self.assertFalse(result.returncode)


if __name__ == '__main__':
    unittest.main()
