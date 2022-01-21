import unittest
import json
from pathlib import Path

import numpy as np

from src.ml.action.update.json.gmsh_scripts import GmshScripts as UpdateJson
from src.ml.variable.categorical import Categorical
from src.ml.variable.continuous import Continuous
from src.ml.variable.discrete import Discrete


class TestOptimize(unittest.TestCase):

    def test_gmsh_scripts_input(self):
        np.random.seed(42)
        variables = [
            {'metadata': {'run': {
                'factory': Categorical(name='factory', choices=['geo', 'occ']),
                'options': {
                    'Mesh.MeshSizeFactor': Continuous(
                        name='Mesh.MeshSizeFactor', low=0.8, high=1.2),
                    'Mesh.MeshSizeExtendFromBoundary': Discrete(
                        name='MeshSizeExtendFromBoundary',
                        low=0, high=2, num=3)}}}}]
        cwd = Path(__file__).parent.resolve()
        path = cwd / '_run_input.json'
        new_path = cwd / '_run_input_new.json'
        a = UpdateJson(path=path,
                       new_path=new_path,
                       variables=variables)
        a()
        with open(new_path) as f:
            d = json.load(f)
        self.assertEqual(d['metadata']['run']['factory'], 'geo')
        self.assertAlmostEqual(d['metadata']['run']['options']['Mesh.MeshSizeFactor'],
                               1.118617194744093)
        self.assertEqual(d['metadata']['run']['options']['Mesh.MeshSizeExtendFromBoundary'],
                         2)


if __name__ == '__main__':
    unittest.main()
