from src.ml.feature.setter.setter import Setter
from src.ml.feature.setter.value import Value
from src.ml.feature.setter.variable import Variable
from src.ml.feature.setter.continuous import Continuous
from src.ml.feature.setter.discrete import Discrete
from src.ml.feature.setter.categorical import Categorical
from src.ml.feature.setter.regex import Regex
from src.ml.feature.setter.regex_file import RegexFile

str2obj = {
    'ml.feature.setter.Setter': Setter,
    'ml.feature.setter.Value': Value,
    'ml.feature.setter.Variable': Variable,
    'ml.feature.setter.Continuous': Continuous,
    'ml.feature.setter.Discrete': Discrete,
    'ml.feature.setter.Categorical': Categorical,
    'ml.feature.setter.Regex': Regex,
    'ml.feature.setter.RegexFile': RegexFile,
}
