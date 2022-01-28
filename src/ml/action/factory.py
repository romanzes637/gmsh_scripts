from src.ml.action.update.json.gmsh_scripts import GmshScripts as JsonGmshScripts
from src.ml.action.read.log.gmsh_scripts import GmshScripts as LogGmshScripts
from src.ml.action.run.gmsh_scripts import GmshScripts as RunGmshScripts
from src.ml.action.action import Action
from src.ml.action.episode import Episode
from src.ml.action.run.command import Command
from src.ml.action.optimize.optuna import Optuna
from src.ml.action.optimize.optuna2 import Optuna2
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
   'ml.action.Action': Action,
   'ml.action.Episode': Episode,
   'ml.action.Command': Command,
   'ml.action.update.json.GmshScripts': JsonGmshScripts,
   'ml.action.read.log.GmshScripts': LogGmshScripts,
   'ml.action.run.GmshScripts': RunGmshScripts,
   'ml.action.optimize.Optuna': Optuna,
   'action.optimize.Optuna2': Optuna2,
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
