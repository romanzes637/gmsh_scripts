import json
from pprint import pprint
from subprocess import Popen
from copy import deepcopy
import itertools
import argparse
import os

# Multiple run of any gmsh scripts
# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--script', help='script filename')
parser.add_argument('-si', '--script_input', help='script input filename')
parser.add_argument('-mi', '--multi_input', help='multi input filename', default='multi_input.json')
parser.add_argument('-l', '--length', help='combinations length', type=int, default=1)
parser.add_argument('-f', '--format', help='mesh format/extension', default='msh')
parser.add_argument('-o', '--prefix', help='output_prefix', default='multi')
args = parser.parse_args()
# Correct arguments
script_path = args.script
basename, extension = os.path.splitext(script_path)
if args.script_input is None:
    args.script_input = '{}_input.json'.format(basename)
script_input_path = args.script_input
multi_input_path = args.multi_input
combination_length = args.length
mesh_format = args.format
output_prefix = args.prefix
pprint(args)
# Get script input
with open(script_input_path) as f:
    script_input = json.load(f)
print('Script Input:')
pprint(script_input)
# Get multi input
with open(multi_input_path) as f:
    multi_input = json.load(f)
print('Multi Input:')
pprint(multi_input)
pids = []
log_paths = []
# Evaluate arguments combinations
args_combinations = itertools.combinations(multi_input, combination_length)
for ac in args_combinations:
    print('Arguments Names: {}'.format(ac))
    # Evaluate values indices combinations
    i_multi_input = {key: range(len(multi_input[key])) for key in ac}  # dict with indices of values
    values_indices_combinations = itertools.product(
        *i_multi_input.values())  # * - unpacking items to separated function arguments
    for vic in values_indices_combinations:
        print('Values Indices: {}'.format(vic))
        vs = []
        # Change script input
        new_script_input = deepcopy(script_input)
        suffix_list = [output_prefix, basename]
        for i, vi in enumerate(vic):
            a = ac[i]
            v = multi_input[a][vi]
            new_script_input[a] = v
            suffix_list.append(a)
            suffix_list.append(str(vi))
            vs.append(v)
        print('Values: {}'.format(vs))
        # Change paths
        path_suffix = '_'.join(suffix_list)
        in_path = '{}_input.json'.format(path_suffix)
        out_path = '{}.{}'.format(path_suffix, mesh_format)
        log_path = 'log_{}'.format(path_suffix)
        print('Path Suffix: {}'.format(path_suffix))
        print('Input File Path: {}'.format(in_path))
        print('Out File Path: {}'.format(out_path))
        print('Log File Path: {}'.format(log_path))
        # Write new args
        with open(in_path, 'w+') as input_file:
            json.dump(new_script_input, input_file, indent=2, sort_keys=True)
        # Run script
        with open(log_path, 'w+') as log_file:
            print(os.path.isfile(in_path))
            process = Popen(['python', script_path, '-i', in_path, '-o', out_path], stdout=log_file, stderr=log_file)
            pids.append(process.pid)
        log_paths.append(os.path.abspath(log_path))
        print('PID: {}'.format(pids[-1]))
# Write ps data
suffix_list = [output_prefix, basename]
path_suffix = '_'.join(suffix_list)
processes_data_path = '{}_processes.json'.format(output_prefix)
processes_data = dict()
for i, p in enumerate(pids):
    data = dict()
    data['log_path'] = os.path.abspath(log_paths[i])
    processes_data[p] = data
with open(processes_data_path, 'w+') as f:
    json.dump(processes_data, f, indent=2, sort_keys=True)
