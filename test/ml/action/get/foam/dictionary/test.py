import unittest
from src.ml.action.get.foam.dictionary import Dictionary


class TestDictionary(unittest.TestCase):

    def assertDictInDict(self, a, b):
        for k, v in a.items():
            if isinstance(v, dict):
                self.assertDictInDict(v, b[k])
            elif isinstance(v, list):
                self.assertListEqual([str(x) for x in v], b[k])
            else:
                self.assertEqual(str(v), b[k])

    def test_t0(self):
        p = '0/T'
        dp = '0_/T_'
        m = {None: {
                'internalField uniform': 7
            }}
        d = Dictionary(p, dump_path=dp, mapping=m, depth=-1)
        d()

    def test_t(self):
        p = 'constant/T'
        dp = 'constant_/T_'
        m = {
            'B-NY': {
                'type': 'convectionFlux',
                'TRef': 100,
                'heatTrans': 5
            }
        }
        d = Dictionary(p, dump_path=dp, mapping=m, depth=-1)
        d()
        d2 = Dictionary.load(dp)
        self.assertDictInDict(m, d2)

    def test_t_prop(self):
        p = 'constant/termProperty'
        dp = 'constant_/termProperty_'
        m = {
            'FeniaFile': {
                'version:': '2.1'},
            'A': {
                'DT': ['1', '2', '3']},
            'B': {
                'rho': 1000,
                'DT': ['3', '2', '1']}
        }
        d = Dictionary(p, dump_path=dp, mapping=m, depth=-1)
        d()
        d2 = Dictionary.load(dp)
        self.assertDictInDict(m, d2)

    def test_fe_solution(self):
        p = 'system/feSolution'
        dp = 'system_/feSolution'
        m = {
            'solvers': {
                'T': {
                    'KSP': 'CG',
                    'rtol': 1e-5},
                'U': {
                    'KSP': 'CG'},
            }}
        d = Dictionary(p, dump_path=dp, mapping=m, depth=-1)
        d()
        d2 = Dictionary.load(dp)
        self.assertDictInDict(m, d2)

    def test_control_dict(self):
        p = 'system/controlDict'
        dp = 'system_/controlDict'
        m = {None: {
            'deltaT': 1.0,
            'dtMax': 100
        }}
        d = Dictionary(p, dump_path=dp, mapping=m, depth=-1)
        d()
        d2 = Dictionary.load(dp)
        self.assertDictInDict(m, d2)


if __name__ == '__main__':
    unittest.main()
