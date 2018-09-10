import json
import shlex
from pprint import pprint
from subprocess import Popen
from copy import deepcopy
import itertools
import argparse
import os

# Multiple run of gmsh scripts
from support import check_file

print('Cmd')
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input filename', required=True)
parser.add_argument('-p', '--prefix', help='prefix', default='multi')
parser.add_argument('-t', '--test', help='test mode', action='store_true')
cmd_args = parser.parse_args()
pprint(cmd_args)
input_path = cmd_args.input
is_test = cmd_args.test
prefix = cmd_args.prefix
print('Input')
with open(input_path) as f:
    input_args = json.load(f)
pprint(input_args)
run_cmd = input_args['arguments']['run_cmd']
print('Inputs')
inputs = dict()
for i in input_args['arguments']['inputs']:
    path = i['path']
    if path not in inputs:
        result = check_file(path)
        print(result)
        with open(result['path']) as f:
            d = json.load(f)
        inputs[path] = d
pprint(inputs)
print('Arguments')
args = list()
for i in input_args['arguments']['inputs']:
    path = i['path']
    for a in i.get('args', list()):
        arg = dict()
        arg['path'] = path
        for name, values in a.items():
            arg['name'] = name
            arg['values'] = values
            args.append(arg)
pprint(args)
print('Values indices')
values_indices = [range(len(x['values'])) for x in args]  # indices of values of args
print(values_indices)
values_combinations = itertools.product(*values_indices)  # * - unpack items as separate func args
pids = list()
logs = list()
for i, vc in enumerate(values_combinations):
    print('Combination {}'.format(i + 1))
    print('Values {}'.format(vc))
    # Make new directory and change cwd to it
    dirname = os.path.join(prefix, str(i + 1))
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    os.chdir(dirname)
    print('cwd: {}'.format(os.getcwd()))
    # Copy all inputs
    for path, d in inputs.items():
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, 'w+') as f:
            json.dump(d, f, indent=2, sort_keys=True)
    # Change inputs
    for j, v in enumerate(vc):
        name = args[j]['name']
        path = args[j]['path']
        value = args[j]['values'][v]
        d = deepcopy(inputs[path])
        d['arguments'][name] = value
        with open(path, 'w') as f:
            json.dump(d, f, indent=2, sort_keys=True)
    # Run
    log = '_'.join(['log', prefix])
    logs.append(os.path.abspath(log))
    if not is_test:
        with open(log, 'w+') as f:
            tokens = shlex.split(run_cmd)
            cmd = ['python']
            cmd.extend(tokens)
            print(cmd)
            process = Popen(cmd, stdout=f, stderr=f)
            pids.append(process.pid)
    else:
        with open(log, 'w+') as f:
            pass
        pids.append(i + 1)
    print('PID: {}'.format(pids[-1]))
    print('log: {}'.format(logs[-1]))
    os.chdir(os.path.join('..', '..'))
print('Number of processes: {}'.format(len(pids)))
dirname = os.path.join(prefix)
os.chdir(dirname)
ps_filename = 'ps.json'
print('Processes file: {}'.format(os.path.abspath(ps_filename)))
ps_data = dict()
for i, p in enumerate(pids):
    d = dict()
    d['log_path'] = os.path.abspath(logs[i])
    ps_data[p] = d
print('Processes data:')
pprint(ps_data)
if not is_test:
    with open(ps_filename, 'w+') as f:
        json.dump(ps_data, f, indent=2, sort_keys=True)
os.chdir(os.path.join('..'))
