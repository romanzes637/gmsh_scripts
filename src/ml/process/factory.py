from src.ml.process.change.json.gmsh_scripts.input import Input
from src.ml.process.process import Process
from src.ml.process.optimize.optuna import Optuna

str2obj = {
   'ml.process.Process': Process,
   'ml.process.change.json.gmsh_scripts.Input': Input,
   'ml.process.optimize.Optuna': Optuna
}
