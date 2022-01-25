import optuna
import mysql.connector
import time
# import plotly


class Objective:
    def __init__(self, min_x, max_x):
        # Hold this implementation specific arguments as the fields of the class.
        self.min_x = min_x
        self.max_x = max_x

    def __call__(self, trial):
        # Calculate an objective value by using the extra arguments.
        trial.set_user_attr("user_value", 42)
        x = trial.suggest_float("x", self.min_x, self.max_x)
        return (x - 2) ** 2


class MultiObjective:
    def __init__(self, min_x, max_x):
        # Hold this implementation specific arguments as the fields of the class.
        self.min_x = min_x
        self.max_x = max_x

    def __call__(self, trial):
        # Calculate an objective value by using the extra arguments.
        trial.set_user_attr("user_value", 42)
        x = trial.suggest_float("x", self.min_x, self.max_x)
        x2 = trial.suggest_float("x2", self.min_x, self.max_x)
        t0 = time.perf_counter()
        y = (x - x2) ** 2
        dt = time.perf_counter() - t0
        return y, dt


def cb(study, trial):  # callback example
    print(len(study.trials))


def create_storage(host='localhost', port='3306', user='root', password='42',
                   db_name='example'):
    con = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        # database=db_name
    )
    cur = con.cursor()
    # cur.execute(f"DROP DATABASE IF EXISTS {db_name}")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    con.close()


def get_storage(host='localhost', port='3306', user='root', password='42',
                dialect_driver='mysql+mysqlconnector',
                db_name='example'):
    return optuna.storages.RDBStorage(
        url=f"{dialect_driver}://{user}:{password}@{host}:{port}/{db_name}")


if __name__ == "__main__":
    # optuna.logging.set_verbosity(optuna.logging.WARNING)
    n_trials = 10
    create_storage()
    storage = get_storage()
    study_name = 'multi_objective'
    # study_name = 'objective'
    if study_name == 'objective':
        objective = Objective(-10, 10)
        direction = 'minimize'
        directions = None
        sampler = optuna.samplers.TPESampler()
    elif study_name == 'multi_objective':
        objective = MultiObjective(-10, 10)
        direction = None
        directions = ['minimize', 'minimize']
        sampler = optuna.samplers.NSGAIISampler()
    else:
        raise ValueError(study_name)
    try:
        study = optuna.create_study(
                storage=storage,
                study_name=study_name,
                load_if_exists=False,
                direction=direction,
                directions=directions,
                pruner=optuna.pruners.MedianPruner(),
                sampler=sampler
            )
    except optuna.exceptions.DuplicatedStudyError as e:
        print(e)
        study = optuna.load_study(
            storage=storage,
            study_name=study_name,
            pruner=optuna.pruners.MedianPruner(),
            sampler=sampler
        )
    study.set_user_attr('user_value', 42)
    study.optimize(objective, n_trials=n_trials, callbacks=[cb])
    if study_name == 'objective':
        fig = optuna.visualization.plot_optimization_history(study)
        fig_slice = optuna.visualization.plot_slice(
            study, params=None, target=None, target_name='Objective Value')
        fig_slice.write_html(f"{study_name}_slice.html")
        fig_contour = optuna.visualization.plot_contour(study, params=None)
        fig_contour.write_html(f"{study_name}_contour.html")
    elif study_name == 'multi_objective':
        # fig = optuna.visualization.plot_optimization_history(
        #     study, target=lambda x: x.values[0], target_name='x')
        fig = optuna.visualization.plot_pareto_front(
            study, target_names=["y", "dt"],
            include_dominated_trials=True, axis_order=[1, 0])
        fig_slice1 = optuna.visualization.plot_slice(
            study, params=None, target=lambda x: x.values[0],
            target_name='y')
        fig_slice1.write_html(f"{study_name}_slice_y.html")
        fig_slice2 = optuna.visualization.plot_slice(
            study, params=None, target=lambda x: x.values[1],
            target_name='dt')
        fig_slice2.write_html(f"{study_name}_slice_dt.html")
        fig_contour1 = optuna.visualization.plot_contour(
            study, params=None, target=lambda x: x.values[0],
            target_name='y')
        fig_contour1.write_html(f"{study_name}_contour_y.html")
        fig_contour2 = optuna.visualization.plot_contour(
            study, params=None, target=lambda x: x.values[1],
            target_name='dt')
        fig_contour2.write_html(f"{study_name}_contour_dt.html")
    else:
        raise ValueError(study_name)
    # fig.write_image(f"{study_name}.png")  # requires the kaleido package
    fig.write_html(f"{study_name}.html")


