import unittest
from src.ml.action.get.foam.dictionary import Dictionary
from src.ml.action.feature.feature import Feature
from src.ml.action.action import Action


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
        f = Feature(post_call=Dictionary(p, dump_path=dp, mapping=m))
        f()

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
        f = Feature(post_call=Dictionary(p, dump_path=dp, mapping=m))
        f()
        d2 = Dictionary.load(dp)
        self.assertDictInDict(m, d2)

    def test_t_prop(self):
        p = 'constant/termProperty'
        dp = 'constant_/termProperty_'
        m = {
            'FeniaFile': {
                'version:': '2.1'},
            'A': {
                'DT': ['1', '2', '{k}']},
            'B': {
                'rho': 1000,
                'DT': ['{k}', '2', '1']}
        }
        f = Feature(
            sup_action=Feature(
                key='sup', value='2.1',
                sup_action=Feature(
                    sup_action=Action(sub_actions=[Feature(key='act_sub', value=2)]),
                    sub_actions=[Feature(key='sup_sup_sub', value=1)]),
                sub_actions=[
                    Feature(key='sup_sub', value='2'),
                    Feature(key='sup_sub2', value='1')
                ]),
            key='k', value=3,
            sub_actions=[
                Feature(key='sub', value='3'),
                Feature(key='sub2', value='1')
            ],
            post_call=Dictionary(p, dump_path=dp, mapping=m))
        f()
        d2 = Dictionary.load(dp)
        m2 = {
            'FeniaFile': {
                'version:': '2.1'},
            'A': {
                'DT': ['1', '2', '3']},
            'B': {
                'rho': 1000,
                'DT': ['3', '2', '1']}
        }
        self.assertDictInDict(m2, d2)

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
        f = Feature(post_call=Dictionary(p, dump_path=dp, mapping=m))
        f()
        d2 = Dictionary.load(dp)
        self.assertDictInDict(m, d2)

    def test_control_dict(self):
        p = 'system/controlDict'
        dp = 'system_/controlDict'
        m = {None: {
            'deltaT': 1.0,
            'dtMax': 100
        }}
        f = Feature(post_call=Dictionary(p, dump_path=dp, mapping=m))
        f()
        d2 = Dictionary.load(dp)
        self.assertDictInDict(m, d2)

    def test_empty(self):
        p = 'empty'
        dp = 'empty_'
        m = {None: {
            'key': 'value',
            'object': {'key2': 'value2'}}
        }
        f = Feature(post_call=Dictionary(p, dump_path=dp, mapping=m))
        f()
        d2 = Dictionary.load(dp)
        self.assertDictInDict(m, d2)


if __name__ == '__main__':
    unittest.main()
