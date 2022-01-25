"""Optuna optimization

Requires optuna https://optuna.readthedocs.io/en/stable/index.html
Requires mysql https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/
Requires mysql-connector-python https://pypi.org/project/mysql-connector-python/
Requires plotly for visualization https://plotly.com/
Parallelization https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/004_distributed.html
Multi-objective https://optuna.readthedocs.io/en/v2.7.0/tutorial/20_recipes/002_multi_objective.html
Pruners https://optuna.readthedocs.io/en/stable/reference/pruners.html#module-optuna.pruners
Samplers https://optuna.readthedocs.io/en/stable/reference/samplers.html#module-optuna.samplers
Nan https://optuna.readthedocs.io/en/stable/faq.html#how-are-nans-returned-by-trials-handled
States https://optuna.readthedocs.io/en/stable/reference/generated/optuna.trial.TrialState.html#optuna.trial.TrialState
TODO sklearn? https://scikit-learn.org/stable/modules/grid_search.html
TODO hyperopt? http://hyperopt.github.io/hyperopt/
"""

import optuna
from copy import deepcopy
from pathlib import Path
import shutil
import os
import uuid

# import mysql.connector

from src.ml.action.action import Action
from src.ml.variable.variable import Variable
from src.ml.variable.categorical import Categorical
from src.ml.variable.continuous import Continuous
from src.ml.variable.discrete import Discrete
from src.ml.variable.fixed import Fixed


class Optuna(Action):
    def __init__(self, tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None,
                 storage=None, study=None, load_if_exists=False, directions=None,
                 actions=None, n_trials=None, work_dir=None, copies=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.storage = storage
        self.study = str(uuid.uuid4()) if study is None else study
        self.load_if_exists = load_if_exists
        self.directions = directions
        self.actions = actions
        self.n_trials = 1 if n_trials is None else n_trials
        self.work_dir = Path().resolve() if work_dir is None else Path(work_dir).resolve()
        self.copies = [] if copies is None else [Path(x).resolve() for x in copies]
        study_dir = self.work_dir / self.study
        self.study_dir = study_dir.resolve()

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            self.study_dir.mkdir(parents=True, exist_ok=True)
            self.study_dir = self.study_dir.resolve()

            def objective(trial):
                trial_dir = self.study_dir / str(trial.number)
                trial_dir = trial_dir.resolve()
                trial_dir.mkdir(parents=True, exist_ok=True)
                for p in self.copies:
                    if p.is_dir():
                        shutil.copytree(p, trial_dir)
                    elif p.is_file():
                        shutil.copy(p, trial_dir)
                    else:
                        raise ValueError(p)
                os.chdir(trial_dir)
                values, variables = {}, {}
                for a in self.actions:
                    if 'ml.action.update.json' in a.__module__:
                        old_variables = deepcopy(a.variables)
                        for v in a.variables:
                            self.set_variable_from_trial(v, trial)
                        vs = a()
                        variables.update(vs)
                        a.variables = old_variables
                    elif 'ml.action.run' in a.__module__:
                        r = a()
                        if r.returncode:
                            return tuple(float('nan')
                                         for _, _ in self.directions.items())
                    elif 'ml.action.read' in a.__module__:
                        vs = a()
                        values.update(vs)
                for k, v in values.items():
                    trial.set_user_attr(k, v)
                return tuple(values[k] for k, v in self.directions.items())
            # get_storage(host='localhost', port='3306', user='root', password='42',
            #             dialect_driver='mysql+mysqlconnector',
            #             db_name='example'):
            # return optuna.storages.RDBStorage(
            #     url=f"{dialect_driver}://{user}:{password}@{host}:{port}/{db_name}")
            # storage = optuna.storages.RDBStorage(self.storage)
            # optuna.logging.set_verbosity(optuna.logging.WARNING)
            if len(self.directions) == 1:
                direction = list(self.directions.values())[0]
                study = optuna.create_study(storage=self.storage,
                                            study_name=self.study,
                                            load_if_exists=self.load_if_exists,
                                            direction=direction)
                study.optimize(objective, n_trials=self.n_trials)
            elif len(self.directions) > 1:  # Multi-objective
                directions = list(self.directions.values())
                study = optuna.create_study(storage=self.storage,
                                            study_name=self.study,
                                            load_if_exists=self.load_if_exists,
                                            directions=directions)
                study.optimize(objective, n_trials=self.n_trials)
            else:
                raise ValueError(self.directions)
            Optuna.plot(study, self.directions, self.study_dir)
            return study.best_trial if len(self.directions) == 1 else study.best_trials

        if self.episode is not None:
            return self.episode(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)

    @staticmethod
    def set_variable_from_trial(d, trial, vs=None):
        vs = {} if vs is None else vs
        for k, v in d.items():
            if isinstance(v, dict):
                Optuna.set_variable_from_trial(v, trial, vs)
            elif isinstance(v, Variable):
                name = v.name
                if isinstance(v, Categorical):
                    v = trial.suggest_categorical(v.name, v.choices)
                elif isinstance(v, Continuous):
                    v = trial.suggest_float(v.name, v.low, v.high)
                elif isinstance(v, Discrete):
                    if isinstance(v.low, int) and isinstance(v.high, int):
                        step = (v.high - v.low) // (v.num - 1)
                        v = trial.suggest_int(v.name, v.low, v.high, step)
                    else:
                        step = (v.high - v.low) / (v.num - 1)
                        v = trial.suggest_float(v.name, v.low, v.high, step)
                elif isinstance(v, Fixed):
                    v = v()  # Sample fixed
                else:
                    raise ValueError(v)
                d[k] = Fixed(name=name, variable=v)
                vs[name] = v
            else:
                raise ValueError(v)
        return vs

    @staticmethod
    def plot(study, directions, path=None):
        p = Path().resolve() if path is None else path
        try:  # required pandas
            study.trials_dataframe().to_csv(p / 'data.csv')
        except Exception as e:
            print(e)
        for i, (n, d) in enumerate(directions.items()):
            try:  # required plotly
                optuna.visualization.plot_optimization_history(
                    study, target_name=n, target=lambda x: x.values[i]).write_html(
                    p / f"optimization_history-{d}-{n}.html")
                optuna.visualization.plot_slice(
                    study, target_name=n, target=lambda x: x.values[i]).write_html(
                    p / f"slice-{d}-{n}.html")
                optuna.visualization.plot_contour(
                    study, target_name=n, target=lambda x: x.values[i]).write_html(
                    p / f"contour-{d}-{n}.html")
                optuna.visualization.plot_parallel_coordinate(
                    study, target_name=n, target=lambda x: x.values[i]).write_html(
                    p / f"parallel_coordinate-{d}-{n}.html")
                optuna.visualization.plot_edf(
                    study, target_name=n, target=lambda x: x.values[i]).write_html(
                    p / f"edf-{d}-{n}.html")
            except Exception as e:
                print(e)
            try:  # required sklearn
                optuna.visualization.plot_param_importances(
                    study, target_name=n, target=lambda x: x.values[i]).write_html(
                    p / f"param_importances-{d}-{n}.html")
            except Exception as e:
                print(e)
        if len(directions) in [2, 3]:
            try:  # required plotly
                ns, ds = list(directions.keys()), list(directions.values())
                optuna.visualization.plot_pareto_front(
                    study, target_names=ns, include_dominated_trials=True).write_html(
                    p / f"_plot_pareto_front-{'-'.join(f'{n}-{d}' for n, d in zip(ns, ds))}.html")
            except Exception as e:
                print(e)

        # def create_storage(host='localhost', port='3306', user='root', password='42',
        #                    db_name='example'):
        #     con = mysql.connector.connect(
        #         host=host,
        #         user=user,
        #         password=password,
        #         port=port,
        #         # database=db_name
        #     )
        #     cur = con.cursor()
        #     # cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
        #     cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        #     con.close()
