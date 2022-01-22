from src.ml.action.update.json.gmsh_scripts import GmshScripts as JsonGmshScripts
from src.ml.action.read.log.gmsh_scripts import GmshScripts as LogGmshScripts
from src.ml.action.run.gmsh_scripts import GmshScripts as RunGmshScripts
from src.ml.action.action import Action
from src.ml.action.state import State
from src.ml.action.run.command import Command
from src.ml.action.optimize.optuna import Optuna


str2obj = {
   'ml.action.Action': Action,
   'ml.action.State': State,
   'ml.action.Command': Command,
   'ml.action.update.json.GmshScripts': JsonGmshScripts,
   'ml.action.read.log.GmshScripts': LogGmshScripts,
   'ml.action.run.GmshScripts': RunGmshScripts,
   'ml.action.optimize.Optuna': Optuna
}
