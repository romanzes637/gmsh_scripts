import unittest
import json
from pathlib import Path

from src.ml.feature.getter.json import Json
from src.ml.feature.feature import Feature


class TestJson(unittest.TestCase):

    def test_update(self):
        r = '\{[A-Za-z0-9\-\_]*\}'

        d, m = {}, {}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {})

        d, m = [], []
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertListEqual(d, [])

        d = [None]
        m = []
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertListEqual(d, [])

        d = []
        m = [None]
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertListEqual(d, [None])

        d = [None]
        m = [None]
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertListEqual(d, [None])

        d = [None, None]
        m = [None]
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertListEqual(d, [None])

        d = [None, None]
        m = [None]
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertListEqual(d, [None])

        d = []
        m = ['{}']
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertListEqual(d, [42])

        d = [24]
        m = ['{}']
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertListEqual(d, [42])

        d = []
        m = ['{}']
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertListEqual(d, [42])

        d = {}
        m = {'a': '{}'}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': 42})

        d = {'b': 24}
        m = {'a': '{}'}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': 42, 'b': 24})

        d = {'a': 24}
        m = {'a': '{}'}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': 42})

        d = {'a': 24}
        m = {'a': '{}'}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': 42})

        d = {'a': 24, 'b': 25}
        m = {'a': '{}'}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': 42, 'b': 25})

        d = {'a': 24, 'b': 25}
        m = {'a': '{}', 'c': ['{}', {'c1': '{}'}, None]}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': 42, 'b': 25, 'c': [42, {'c1': 42}, None]})

        d = {'a': {'aa': 24}, 'b': ['b1', {'b2': {'b2b2': 33}}, 'b3']}
        m = {'a': {'aa': '{}'}}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': {'aa': 42}, 'b': ['b1', {'b2': {'b2b2': 33}}, 'b3']})

        d = {'a': {'aa': 24}, 'b': ['b1', {'b2': {'b2b2': 33}}, 'b3']}
        m = {'b': ['{}', None, None]}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': {'aa': 24}, 'b': [42, {'b2': {'b2b2': 33}}, 'b3']})

        d = [['a1', 'a2'], {'b': {'bb': {'bbb': 24}}}]
        m = [[None, '{}'], {'b': {'bb': {'bbb': '{}'}}}]
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertListEqual(d, [['a1', 42], {'b': {'bb': {'bbb': 42}}}])

        d = {'a': [[[24]]]}
        m = {'a': [None]}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': [[[24]]]})

        d = {'a': [[[24]]]}
        m = {'a': [[['{}']]]}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': [[[42]]]})

        d = {'a': 24}
        m = {'a': '{}{}'}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': 4242})

        d = {'a': 24}
        m = {'a': '{}-{}'}
        f = Feature(key='feature', value=42)
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': '42-42'})

        d = {'a': 24}
        m = {'a': '{0}-{1}'}
        f = Feature(key='feature', value=[30, 20])
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': '30-20'})

        d = {'a': 24}
        m = {'a': '{hello_}-{world-}'}
        f = Feature(key='feature', value={'hello_': 0, 'world-': 1})
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': '0-1'})

        d = {'a': 24}
        m = {'a': '{hello_};{world-};{MAN}'}
        f = Feature(key='feature', value={'hello_': 0, 'world-': 1, 'MAN': 'DO'})
        d = Json.update(d, m, f, r)
        self.assertDictEqual(d, {'a': '0;1;DO'})

    def test_file(self):
        d = {'a': 24}
        m = {'a': '{hello_};{world-};{MAN}'}
        p = 'd.json'
        with open(p, 'w') as f:
            json.dump(d, f)
        j = Json(path=p, mapping=m)
        f = Feature(key='feature',
                    value={'hello_': 0, 'world-': 1, 'MAN': 'DO'},
                    getter=j)
        f.get()
        with open(p) as f:
            d = json.load(f)
        self.assertDictEqual(d, {'a': '0;1;DO'})
        p = Path(p)
        p.unlink()
        self.assertFalse(p.exists())


if __name__ == '__main__':
    unittest.main()
