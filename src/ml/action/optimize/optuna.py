"""Optuna optimization pipeline

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
TODO multiprocessing logging (frozen by now) https://optuna.readthedocs.io/en/latest/faq.html#how-to-suppress-log-messages-of-optuna
"""
from pathlib import Path
import shutil
import uuid
import logging
import concurrent.futures
import os
from itertools import combinations
import time
import sys

import optuna

from src.ml.action.action import Action
from src.ml.action.feature.feature import Feature
from src.ml.action.run.run import Run
from src.ml.action.set.value import Value
from src.ml.action.set.continuous import Continuous
from src.ml.action.set.categorical import Categorical
from src.ml.action.set.discrete import Discrete


class Optuna(Action):
    """Optuna optimization action

    Args:
        storage (str): dialect+driver://username:password@host:port/database
            see SQLAlchemy https://docs.sqlalchemy.org/en/14/core/engines.html
    """

    def __init__(self, storage=None, study_name=None, load_if_exists=None,
                 n_trials=None, optimize_timeout=None,
                 do_delete_study=None, do_write_results=None,
                 sampler=None, sampler_kwargs=None,
                 pruner=None, pruner_kwargs=None,
                 objectives=None, constraints=None,
                 copies=None, links=None,
                 do_optimize=None, optimize_path=None,
                 optimize_executor=None, optimize_executor_kwargs=None,
                 do_update_sub_actions=None, update_trial_number=None, do_sub_call=None,
                 color_key=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.study_name = str(uuid.uuid4()) if study_name is None else study_name
        self.load_if_exists = True if load_if_exists is None else load_if_exists
        self.delete_study = False if do_delete_study is None else do_delete_study
        self.objectives = {} if objectives is None else objectives
        self.constraints = {} if constraints is None else constraints
        self.n_trials = n_trials
        self.optimize_timeout = optimize_timeout
        self.copies = [] if copies is None else [Path(x).resolve() for x in copies]
        self.links = [] if links is None else [Path(x).resolve() for x in links]
        self.sampler = sampler
        self.sampler_kwargs = {} if sampler_kwargs is None else sampler_kwargs
        self.pruner = pruner
        self.pruner_kwargs = {} if pruner_kwargs is None else pruner_kwargs
        self.do_optimize = True if do_optimize is None else do_optimize
        self.optimize_path = Path(str(uuid.uuid4())).resolve() if optimize_path is None else Path(optimize_path).resolve()
        self.optimize_executor = optimize_executor
        self.optimize_executor_kwargs = optimize_executor_kwargs
        study_dir = self.optimize_path / self.study_name
        self.study_dir = study_dir.resolve()
        self.do_update_sub_actions = False if do_update_sub_actions is None else do_update_sub_actions
        self.update_trial_number = update_trial_number
        self.do_sub_call = False if do_sub_call is None else do_sub_call
        self.do_write_results = True if do_write_results is None else do_write_results
        self.color_key = color_key

    class Objective:
        def __init__(self, optuna_action=None):
            self.optuna_action = optuna_action

        def __call__(self, trial):
            # TODO multiprocessing logging
            if self.optuna_action.optimize_executor is not None:
                optuna.logging.set_verbosity(optuna.logging.WARNING)
            trial_dir = self.optuna_action.study_dir / str(trial.number)
            trial_dir = trial_dir.resolve()
            trial_dir.mkdir(parents=True, exist_ok=True)
            for p in self.optuna_action.copies:
                if p.is_dir():
                    shutil.copytree(p, trial_dir)
                elif p.is_file():
                    shutil.copy(p, trial_dir)
                else:
                    raise ValueError(p)
            for link in self.optuna_action.links:
                if link.is_dir():
                    os.symlink(link, trial_dir / link.name,
                               target_is_directory=True)
                elif link.is_file():
                    os.symlink(link, trial_dir / link.name,
                               target_is_directory=False)
                else:
                    raise ValueError(link)
            os.chdir(trial_dir)
            # Do
            fs = []  # features
            for a in self.optuna_action.sub_actions:
                if isinstance(a, Feature):
                    s = a.setter
                    if isinstance(s, Continuous):
                        a.setter = Value(value=trial.suggest_float(
                            name=a.key, low=s.low, high=s.high))
                    elif isinstance(s, Categorical):
                        a.setter = Value(value=trial.suggest_categorical(
                            name=a.key, choices=s.choices))
                    elif isinstance(s, Discrete):
                        if isinstance(s.low, int) and isinstance(s.high, int):
                            step = (s.high - s.low) // (s.num - 1)
                            v = trial.suggest_int(
                                name=a.key, low=s.low, high=s.high, step=step)
                        else:
                            step = (s.high - s.low) / (s.num - 1)
                            v = trial.suggest_float(
                                name=a.key, low=s.low, high=s.high, step=step)
                        a.setter = Value(value=v)
                    a()
                    a.setter = s
                    trial.set_user_attr(a.key, a.value)
                    if a.key in self.optuna_action.constraints:
                        if not a.value:
                            return float('nan')
                    fs.append(a)
                elif isinstance(a, Run):
                    r, _ = a()
                    if r.returncode != 0:
                        return float('nan')
            fs_map = {x.key: x.value for x in fs}
            return tuple(fs_map.get(k, float('nan'))
                         for k, v in self.optuna_action.objectives.items())

    def pre_call(self, action=None, *args, **kwargs):
        root = Path().resolve()
        if self.delete_study:
            optuna.delete_study(study_name=self.study_name, storage=self.storage)
            return self, action
        self.study_dir.mkdir(parents=True, exist_ok=True)
        self.study_dir = self.study_dir.resolve()
        if self.do_optimize:
            if self.optimize_executor is None:
                optuna.logging.enable_propagation()  # Propagate logs to the root logger.
                optuna.logging.disable_default_handler()  # Stop showing logs in sys.stderr.
                study = self.create_study()
                study.optimize(func=self.Objective(self),
                               n_trials=self.n_trials,
                               timeout=self.optimize_timeout)
            else:
                executor = getattr(concurrent.futures, self.optimize_executor)
                try:
                    with executor(**self.optimize_executor_kwargs) as e:
                        # TODO multiprocessing logging
                        # optuna.logging.disable_default_handler()
                        # logger = logging.getLogger()
                        # default_handler = logger.handlers[0]
                        # optuna.logging.enable_propagation()  # Propagate logs to the root logger.
                        # optuna.logging.disable_default_handler()  # Stop showing logs in sys.stderr.
                        # log_path = self.study_dir / f'study.log'
                        # logger = logging.getLogger()
                        # logger.handlers = []
                        # logger.addHandler(logging.FileHandler(log_path))
                        # TODO n_jobs == max_workers of executor?
                        optuna.logging.set_verbosity(optuna.logging.WARNING)
                        fs = (e.submit(
                            self.create_study().optimize,
                            func=self.Objective(self),
                            n_trials=self.n_trials)
                            for _ in range(e._max_workers))
                        for f in concurrent.futures.as_completed(
                                fs=fs, timeout=self.optimize_timeout):
                            f.result()
                except concurrent.futures.TimeoutError as timeout_error:
                    logging.warning(timeout_error)
                study = self.create_study()  # For write
        else:
            optuna.logging.enable_propagation()  # Propagate logs to the root logger.
            optuna.logging.disable_default_handler()  # Stop showing logs in sys.stderr.
            study = self.create_study()
        if self.do_write_results:
            self.write_results(study)
        os.chdir(root)
        if self.do_update_sub_actions:
            self.update_sub_actions(study)
        return self, action

    def sub_call(self, action=None, *args, **kwargs):
        if self.do_sub_call:
            return super().sub_call(action=action, *args, **kwargs)
        else:
            return self, action

    def create_study(self):
        if self.sampler is not None:
            sampler = getattr(optuna.samplers, self.sampler)(**self.sampler_kwargs)
        else:
            sampler = None
        if self.pruner is not None:
            pruner = getattr(optuna.pruners, self.pruner)(**self.pruner_kwargs)
        else:
            pruner = None
        if len(self.objectives) == 1:
            direction = list(self.objectives.values())[0]
            study = optuna.create_study(storage=self.storage,
                                        study_name=self.study_name,
                                        load_if_exists=self.load_if_exists,
                                        sampler=sampler,
                                        pruner=pruner,
                                        direction=direction)
        elif len(self.objectives) > 1:  # Multi-objective
            directions = list(self.objectives.values())
            study = optuna.create_study(storage=self.storage,
                                        study_name=self.study_name,
                                        load_if_exists=self.load_if_exists,
                                        sampler=sampler,
                                        pruner=pruner,
                                        directions=directions)
        else:
            raise ValueError(self.objectives)
        return study

    def update_sub_actions(self, study):
        if len(study.trials) == 0:
            logging.warning(f'No trials in study {self.study_name} for update!')
            return
        if self.update_trial_number is None:  # Choose best
            if study.directions is not None:
                if len(study.best_trials) > 0:
                    trial = study.best_trials[0]
                else:
                    trial = None
            elif study.direction is not None:
                trial = study.best_trial
            else:
                trial = None
        else:  # update_trial_number is index
            if self.update_trial_number < len(study.trials):
                trial = study.trials[self.update_trial_number]
            else:
                trial = None
        if trial is not None:
            for a in self.sub_actions:
                if isinstance(a, Feature):
                    if a.key in trial.params:
                        v = trial.params[a.key]
                        a.setter = Value(value=v)

    def write_results(self, study):
        if len(study.trials) == 0:
            logging.warning(f'No trials in study {self.study_name} to write!')
            return
        p = self.study_dir
        try:  # required pandas
            study.trials_dataframe().to_csv(p / 'data.csv')
        except Exception as e:
            print(e)
        # Pareto front
        if len(self.objectives) > 1:
            try:  # required plotly
                import plotly.express as px

                n = len(self.objectives)
                ns = list(self.objectives.keys())
                ds = list(self.objectives.values())
                df = study.trials_dataframe()
                old2new = {f'values_{i}': f'values_{x}' for i, x in enumerate(ns)}
                df = df.rename(columns=old2new)
                hover_data = [x for x in df.columns
                              if x.startswith('params_')
                              or x.startswith('values_')
                              or (x.startswith('user_attrs_') and 'time' not in x)
                              or x == 'duration']
                if self.color_key is not None:
                    color = f'user_attrs_{self.color_key}'
                else:
                    color = None
                for c in combinations(range(n), 2):
                    c_vs = [old2new[f'values_{x}'] for x in c]
                    c_ns = [ns[x] for x in c]
                    c_ds = [ds[x] for x in c]
                    labels = dict(zip(c_vs, c_ns))
                    fig = px.scatter(
                        df, x=c_vs[0], y=c_vs[1],
                        color=color,
                        hover_name="number",
                        hover_data=hover_data,
                        labels=labels)
                    if color is not None:
                        fig.layout.coloraxis.colorbar.title = color
                    fig.write_html(p / f"pareto_front-{'-'.join(f'{n}-{d}' for n, d in zip(c_ns, c_ds))}.html")
                for c in combinations(range(n), 3):
                    c_vs = [old2new[f'values_{x}'] for x in c]
                    c_ns = [ns[x] for x in c]
                    c_ds = [ds[x] for x in c]
                    labels = dict(zip(c_vs, c_ns))
                    fig = px.scatter_3d(
                        df, x=c_vs[0], y=c_vs[1], z=c_vs[2],
                        color=color,
                        hover_name="number",
                        hover_data=hover_data,
                        labels=labels)
                    if color is not None:
                        fig.layout.coloraxis.colorbar.title = color
                    fig.write_html(p / f"pareto_front-{'-'.join(f'{n}-{d}' for n, d in zip(c_ns, c_ds))}.html")
            except Exception as e:
                print(e)
        for i, (n, d) in enumerate(self.objectives.items()):
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
