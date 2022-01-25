from src.ml.variable.variable import Variable
from src.ml.variable.categorical import Categorical
from src.ml.variable.continuous import Continuous
from src.ml.variable.discrete import Discrete
from src.ml.variable.fixed import Fixed

str2obj = {
    'ml.variable.Variable': Variable,
    'ml.variable.Categorical': Categorical,
    'ml.variable.Continuous': Continuous,
    'ml.variable.Discrete': Discrete,
    'ml.variable.Fixed': Fixed,
}
