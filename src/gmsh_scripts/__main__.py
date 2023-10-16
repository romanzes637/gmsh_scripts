import argparse

from gmsh_scripts.run import main as main_run

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input')
    parser.add_argument('--plot', help='plot graph only', action='store_true')
    args = vars(parser.parse_known_args()[0])
    if args['plot']:
        from gmsh_scripts.plot import main as main_plot
        main_plot()
    else:
        main_run()
