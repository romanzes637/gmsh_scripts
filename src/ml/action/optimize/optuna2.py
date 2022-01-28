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

from src.ml.action.action import Action
from src.ml.action.feature.feature import Feature
from src.ml.action.run.run import Run
from src.ml.action.set.value import Value
from src.ml.action.set.continuous import Continuous
from src.ml.action.set.categorical import Categorical
from src.ml.action.set.discrete import Discrete


class Optuna2(Action):
    """Optuna optimization action

    Args:
        storage (str): dialect+driver://username:password@host:port/database
            see SQLAlchemy https://docs.sqlalchemy.org/en/14/core/engines.html
        constraints (dict): {name: [[operator, value], [operator], ...]}
            see https://docs.python.org/3/library/operator.html#mapping-operators-to-functions
    """

    def __init__(self, storage=None, study=None, load_if_exists=False, objectives=None,
                 constraints=None, delete_study=False, write_study=False,
                 actions=None, n_trials=None, work_dir=None, copies=None,
                 optimize_executor=None, optimize_max_workers=None,
                 optimize_n_jobs=None, timeout=None,
                 tag=None, subactions=None, executor=None,
                 episode=None, do_propagate_episode=None):
        super().__init__(tag=tag, subactions=subactions, executor=executor,
                         episode=episode, do_propagate_episode=do_propagate_episode)
        self.storage = storage
        self.study = str(uuid.uuid4()) if study is None else study
        self.load_if_exists = load_if_exists
        self.objectives = objectives
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
            # Do
            fs = []  # features
            for a in self.optuna_action.actions:
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
                    if a.key in self.optuna_action.constraints:
                        if not a.value:
                            return float('nan')
                    fs.append(a)
                elif isinstance(a, Run):
                    r = a()
                    if r.returncode != 0:
                        return float('nan')
            fs_map = {x.key: x.value for x in fs}
            for k, v in fs_map.items():
                trial.set_user_attr(k, v)
            return tuple(fs_map.get(k, float('nan'))
                         for k, v in self.optuna_action.objectives.items())

    def __call__(self, *args, **kwargs):
        def call(self, *args, **kwargs):
            if self.delete_study:
                optuna.delete_study(study_name=self.study, storage=self.storage)
                return None
            self.study_dir.mkdir(parents=True, exist_ok=True)
            self.study_dir = self.study_dir.resolve()
            if self.write_study:
                study = self.create_study()  # For write
                self.write(study, self.objectives, self.study_dir)
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
            self.write(study, self.objectives, self.study_dir)
            return study.best_trial if len(self.objectives) == 1 else study.best_trials

        if self.episode is not None:
            return self.episode(call)(self, *args, **kwargs)
        else:
            return call(self, *args, **kwargs)

    def create_study(self):
        if len(self.objectives) == 1:
            direction = list(self.objectives.values())[0]
            study = optuna.create_study(storage=self.storage,
                                        study_name=self.study,
                                        load_if_exists=self.load_if_exists,
                                        direction=direction)
        elif len(self.objectives) > 1:  # Multi-objective
            directions = list(self.objectives.values())
            study = optuna.create_study(storage=self.storage,
                                        study_name=self.study,
                                        load_if_exists=self.load_if_exists,
                                        directions=directions)
        else:
            raise ValueError(self.objectives)
        return study

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
