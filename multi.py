import json
from pprint import pprint
from subprocess import Popen
from copy import deepcopy
import itertools
import argparse
import os

# Multiple run of gmsh scripts
# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--script', help='script filename')
parser.add_argument('-si', '--script_input', help='script input filename')
parser.add_argument('-i', '--input', help='input filename', default='input_multi.json')
parser.add_argument('-l', '--length', help='combinations length', type=int, default=1)
parser.add_argument('-f', '--format', help='mesh format/extension', default='msh')
parser.add_argument('-p', '--prefix', help='output_prefix', default='multi')
parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
parser.add_argument('-t', '--test', help='test mode, no processes starting', action='store_true')
args = parser.parse_args()
# Correct arguments
basename, extension = os.path.splitext(args.script)
if args.script_input is None:
    args.script_input = '{}_input.json'.format(basename)
print('Arguments:')
pprint(args)
# Parameters initialization
script_path = args.script
script_input_path = args.script_input
input_path = args.input
length = args.length
mesh_format = args.format
prefix = args.prefix
is_test = args.test
is_verbose = args.verbose
# Get script input
with open(script_input_path) as f:
    script_input = json.load(f)
print('Script Input from {}:'.format(script_input_path))
pprint(script_input)
# Get multi input
with open(input_path) as f:
    multi_input = json.load(f)
print('Input from {}:'.format(input_path))
pprint(multi_input)
pids = []
log_paths = []
# Evaluate arguments combinations
args_combinations = itertools.combinations(multi_input, length)
for j, ac in enumerate(args_combinations):
    # Evaluate values indices combinations
    i_multi_input = {key: range(len(multi_input[key])) for key in ac}  # dict with indices of values
    values_indices_combinations = itertools.product(*i_multi_input.values())  # * - unpack items as separate func args
    for vic in values_indices_combinations:
        print('\tArguments Combination {} Values Combination {}'.format(j + 1, len(pids) + 1))
        print('Arguments:\n{}'.format(ac))
        print('Values Indices:\n{}'.format(vic))
        vs = []
        # Change script input
        new_script_input = deepcopy(script_input)
        suffix_list = [prefix, basename]
        for i, vi in enumerate(vic):
            a = ac[i]
            v = multi_input[a][vi]
            new_script_input[a] = v
            suffix_list.append(a)
            suffix_list.append(str(vi))
            vs.append(v)
        print('Values:\n{}'.format(vs))
        # Change paths
        path_suffix = '_'.join(suffix_list)
        in_path = 'input_{}.json'.format(path_suffix)
        out_path = '{}.{}'.format(path_suffix, mesh_format)
        log_path = 'log_{}'.format(path_suffix)
        print('Path Suffix:\n{}'.format(path_suffix))
        print('Input File Path:\n{}'.format(in_path))
        print('Out File Path:\n{}'.format(out_path))
        print('Log File Path:\n{}'.format(log_path))
        log_paths.append(os.path.abspath(log_path))
        if not is_test:
            # Write new script input file
            with open(in_path, 'w+') as script_input_file:
                json.dump(new_script_input, script_input_file, indent=2, sort_keys=True)
            # Run script
            with open(log_path, 'w+') as log_file:
                cmd = ['python', script_path, '-i', in_path, '-o', out_path]
                if is_verbose:
                    cmd.append('-v')
                print(cmd)
                process = Popen(cmd, stdout=log_file, stderr=log_file)
                pids.append(process.pid)
        else:
            if len(pids) > 0:
                pids.append(pids[-1] + 1)
            else:
                pids.append(0)
        print('PID:\n{}'.format(pids[-1]))
print('\tNumber of processes: {}'.format(len(pids)))
# Write processes data
suffix_list = [prefix, basename]
path_suffix = '_'.join(suffix_list)
processes_path = 'processes_{}.json'.format(path_suffix)
print('Processes File Path:\n{}'.format(processes_path))
processes_data = dict()
for i, p in enumerate(pids):
    d = dict()
    d['log_path'] = os.path.abspath(log_paths[i])
    processes_data[p] = d
print('Processes data:')
pprint(processes_data)
if not is_test:
    with open(processes_path, 'w+') as f:
        json.dump(processes_data, f, indent=2, sort_keys=True)
