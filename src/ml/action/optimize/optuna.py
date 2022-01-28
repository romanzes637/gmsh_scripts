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
import optuna
from copy import deepcopy
from pathlib import Path
import shutil
import os
import uuid
import logging
import concurrent.futures
import operator
import os
from itertools import combinations

# import mysql.connector

from src.ml.action.action import Action
from src.ml.variable.variable import Variable
from src.ml.variable.categorical import Categorical
from src.ml.variable.continuous import Continuous
from src.ml.variable.discrete import Discrete
from src.ml.variable.fixed import Fixed


class Optuna(Action):
    """Optuna optimization action

    Args:
        storage (str): dialect+driver://username:password@host:port/database
            see SQLAlchemy https://docs.sqlalchemy.org/en/14/core/engines.html
        constraints (dict): {name: [[operator, value], [operator], ...]}
            see https://docs.python.org/3/library/operator.html#mapping-operators-to-functions
    """

    def __init__(self, tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None,
                 storage=None, study=None, load_if_exists=False, directions=None,
                 constraints=None, delete_study=False, write_study=False,
                 actions=None, n_trials=None, work_dir=None, copies=None,
                 optimize_executor=None, optimize_max_workers=None,
                 optimize_n_jobs=None, timeout=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.storage = storage
        self.study = str(uuid.uuid4()) if study is None else study
        self.load_if_exists = load_if_exists
        self.directions = directions
        self.constraints = {} if constraints is None else constraints
        self.actions = actions
        self.n_trials = 1 if n_trials is None else n_trials
        self.work_dir = Path().resolve() if work_dir is None else Path(work_dir).resolve()
        self.copies = [] if copies is None else [Path(x).resolve() for x in copies]
        study_dir = self.work_dir / self.study
        self.study_dir = study_dir.resolve()
        self.optimize_executor = optimize_executor
        self.optimize_max_workers = optimize_max_workers
        self.optimize_n_jobs = 1 if optimize_n_jobs is None else optimize_n_jobs
        self.timeout = timeout
        self.delete_study = delete_study
        self.write_study = write_study

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
            os.chdir(trial_dir)
            values, variables = {}, {}
            for a in self.optuna_action.actions:
                if 'ml.action.update.json' in a.__module__:
                    old_variables = deepcopy(a.variables)
                    for v in a.variables:
                        self.optuna_action.set_setter_from_trial(v, trial)
                    vs = a()
                    if not self.optuna_action.check_constraints(self.optuna_action.constraints, vs):
                        return tuple(float('nan') for _ in self.optuna_action.directions)
                    variables.update(vs)
                    a.variables = old_variables
                elif 'ml.action.run' in a.__module__:
                    r = a()
                    if r.returncode:
                        return tuple(float('nan') for _ in self.optuna_action.directions)
                elif 'ml.action.read' in a.__module__:
                    vs = a()
                    if not self.optuna_action.check_constraints(self.optuna_action.constraints, vs):
                        return tuple(float('nan') for _ in self.optuna_action.directions)
                    values.update(vs)
            for k, v in values.items():
                trial.set_user_attr(k, v)
            return tuple(values.get(k, float('nan')) for k, v in self.optuna_action.directions.items())

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            if self.delete_study:
                optuna.delete_study(study_name=self.study, storage=self.storage)
                return None
            self.study_dir.mkdir(parents=True, exist_ok=True)
            self.study_dir = self.study_dir.resolve()
            if self.write_study:
                study = self.create_study()  # For write
                self.write(study, self.directions, self.study_dir)
                return None
            # optuna.logging.disable_default_handler()
            # logger = logging.getLogger()
            # default_handler = logger.handlers[0]
            # optuna.logging.enable_propagation()  # Propagate logs to the root logger.
            # optuna.logging.disable_default_handler()  # Stop showing logs in sys.stderr.
            # log_path = self.study_dir / f'study.log'
            # logger = logging.getLogger()
            # logger.handlers = []
            # logger.addHandler(logging.FileHandler(log_path))
            if self.optimize_executor == 'thread':
                executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=self.optimize_max_workers)
            elif self.optimize_executor == 'process':
                executor = concurrent.futures.ProcessPoolExecutor(
                    max_workers=self.optimize_max_workers)
            else:  # consecutive
                executor = None
            if executor is not None:
                # TODO multiprocessing logging
                optuna.logging.set_verbosity(optuna.logging.WARNING)
                # TODO as_completed timeout?
                futures = (concurrent.futures.as_completed(executor.submit(
                    self.create_study().optimize,
                    func=self.Objective(self),
                    n_trials=self.n_trials,
                    timeout=self.timeout) for _ in range(self.optimize_n_jobs)))
                for future in futures:
                    future.result()
                executor.shutdown()
                study = self.create_study()  # For write
            else:
                # TODO multiprocessing logging
                optuna.logging.enable_propagation()  # Propagate logs to the root logger.
                optuna.logging.disable_default_handler()  # Stop showing logs in sys.stderr.
                study = self.create_study()
                study.optimize(func=self.Objective(self),
                               n_trials=self.n_trials,
                               timeout=self.timeout)
            # TODO multiprocessing logging
            # logger.handlers = []
            # logger.addHandler(default_handler)
            self.write(study, self.directions, self.study_dir)
            return study.best_trial if len(self.directions) == 1 else study.best_trials

        if self.episode is not None:
            return self.episode(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)

    def create_study(self):
        if len(self.directions) == 1:
            direction = list(self.directions.values())[0]
            study = optuna.create_study(storage=self.storage,
                                        study_name=self.study,
                                        load_if_exists=self.load_if_exists,
                                        direction=direction)
        elif len(self.directions) > 1:  # Multi-objective
            directions = list(self.directions.values())
            study = optuna.create_study(storage=self.storage,
                                        study_name=self.study,
                                        load_if_exists=self.load_if_exists,
                                        directions=directions)
        else:
            raise ValueError(self.directions)
        return study

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
    def check_constraints(cs, vs):
        """Check values/variables on constraints

        Args:
            cs (dict): constraints - {name: [[operator, value], [operator], ...]}
                see https://docs.python.org/3/library/operator.html#mapping-operators-to-functions
            vs (dict): variables/values - {name: value}

        Returns:
            bool: check result
        """
        for k, v in vs.items():
            if k in cs:
                cs_k = cs[k]
                for c in cs_k:
                    if len(c) == 2:  # binary operator
                        o, v2 = getattr(operator, c[0]), c[1]
                        r = o(v, v2)
                    elif len(c) == 1:  # unary operator
                        o = getattr(operator, c[0])
                        r = o(v)
                    else:
                        raise ValueError(cs, vs, k, v, c)
                    if not r:
                        return False
        return True

    @staticmethod
    def write(study, directions, path=None):
        """Write study data and visualization

        Args:
            study:
            directions:
            path:
        """
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
        try:  # required plotly
            import plotly.express as px

            n = len(directions)
            ns = list(directions.keys())
            ds = list(directions.values())
            df = study.trials_dataframe()
            old2new = {f'values_{i}': f'values_{x}' for i, x in enumerate(ns)}
            df = df.rename(columns=old2new)
            hover_data = [x for x in df.columns
                          if x.startswith('params_')
                          or x.startswith('values_')
                          or (x.startswith('user_attrs_') and 'time' not in x)
                          or x == 'duration']
            for c in combinations(range(n), 2):
                c_vs = [old2new[f'values_{x}'] for x in c]
                c_ns = [ns[x] for x in c]
                c_ds = [ds[x] for x in c]
                labels = dict(zip(c_vs, c_ns))
                fig = px.scatter(
                    df, x=c_vs[0], y=c_vs[1],
                    color='user_attrs_elements',
                    hover_name="number",
                    hover_data=hover_data,
                    labels=labels)
                fig.layout.coloraxis.colorbar.title = 'elements'
                fig.write_html(p / f"pareto_front-{'-'.join(f'{n}-{d}' for n, d in zip(c_ns, c_ds))}.html")
            for c in combinations(range(n), 3):
                c_vs = [old2new[f'values_{x}'] for x in c]
                c_ns = [ns[x] for x in c]
                c_ds = [ds[x] for x in c]
                labels = dict(zip(c_vs, c_ns))
                fig = px.scatter_3d(
                    df, x=c_vs[0], y=c_vs[1], z=c_vs[2],
                    color='user_attrs_elements',
                    hover_name="number",
                    hover_data=hover_data,
                    labels=labels)
                fig.layout.coloraxis.colorbar.title = 'elements'
                fig.write_html(p / f"pareto_front-{'-'.join(f'{n}-{d}' for n, d in zip(c_ns, c_ds))}.html")
        except Exception as e:
            print(e)
        # if len(directions) in [2, 3]:
        #     try:  # required plotly
        #         ns, ds = list(directions.keys()), list(directions.values())
        #         optuna.visualization.plot_pareto_front(
        #             study, target_names=ns, include_dominated_trials=True).write_html(
        #             p / f"pareto_front-{'-'.join(f'{n}-{d}' for n, d in zip(ns, ds))}.html")
        #     except Exception as e:
        #         print(e)
        # else:
