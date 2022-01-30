from src.ml.action.action import Action
from src.ml.action.episode.episode import Episode
from src.ml.action.sleep.sleep import Sleep
from src.ml.action.run.gmsh_scripts import GmshScripts as RunGmshScripts
from src.ml.action.run.subprocess import Subprocess
from src.ml.action.optimize.optuna import Optuna
from src.ml.action.feature.feature import Feature
from src.ml.action.set.set import Set
from src.ml.action.set.value import Value
from src.ml.action.set.variable import Variable
from src.ml.action.set.continuous import Continuous
from src.ml.action.set.discrete import Discrete
from src.ml.action.set.categorical import Categorical
from src.ml.action.set.regex import Regex as SetRegex
from src.ml.action.set.regex_file import RegexFile as SetRegexFile
from src.ml.action.set.equation import Equation
from src.ml.action.get.get import Get
from src.ml.action.get.json import Json

str2obj = {
    'action.Action': Action,
    'action.Episode': Episode,
    'action.Sleep': Sleep,
    'action.Subprocess': Subprocess,
    'action.run.GmshScripts': RunGmshScripts,
    'action.optimize.Optuna': Optuna,
    'action.Feature': Feature,
    'action.setter.Set': Set,
    'action.setter.Value': Value,
    'action.setter.Variable': Variable,
    'action.setter.Continuous': Continuous,
    'action.setter.Discrete': Discrete,
    'action.setter.Categorical': Categorical,
    'action.setter.Regex': SetRegex,
    'action.setter.RegexFile': SetRegexFile,
    'action.setter.Equation': Equation,
    'action.getter.Get': Get,
    'action.getter.Json': Json,
}
