"""Multivariate launch of gmsh scripts.
    Positional arguments:
        input filename
    Keyword arguments:
        p or --prefix -- prefix to results folder name (default multi)
        t or --test -- test mode (default False)
        w or --test -- wait for end of all subprocesses (default False)
"""

if __name__ == '__main__':
    import argparse
    import os
    import json
    import itertools
    import shlex
    from subprocess import Popen
    from pprint import pprint
    import platform

    from support import check_file

    print(platform.uname())
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input filename')
    parser.add_argument('-p', '--prefix', help='prefix', default='multi')
    parser.add_argument('-t', '--test', help='test mode', action='store_true')
    parser.add_argument('-w', '--wait', help='wait for end of all subprocesses',
                        action='store_true')
    cmd_args = parser.parse_args()
    print('Args')
    pprint(cmd_args)
    input_path = cmd_args.input
    is_test = cmd_args.test
    prefix = cmd_args.prefix
    filename, extension = os.path.splitext(os.path.basename(input_path))
    prefix = '_'.join([prefix, filename])
    print('Prefix')
    print(prefix)
    print('Input')
    with open(input_path) as f:
        input_args = json.load(f)
    pprint(input_args)
    run_cmd = input_args['arguments']['run_cmd']
    print('Inputs')
    inputs = dict()
    for c_i in input_args['arguments']['inputs']:
        path = c_i['path']
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
    print('Args indices')
    args_indices = [range(len(x['values'])) for x in args]
    print(args_indices)
    args_combinations = itertools.product(*args_indices)
    pids = list()
    logs = list()
    processes = set()
    for c_i, c in enumerate(args_combinations):
        print('Combination {}'.format(c_i + 1))
        print('Values {}'.format(c))
        # Make new directory and change cwd to it
        dirname = os.path.join(prefix, str(c_i + 1))
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
        for a_i, v_i in enumerate(c):
            print('argument {} value {}'.format(a_i, v_i))
            name = args[a_i]['name']
            path = args[a_i]['path']
            value = args[a_i]['values'][v_i]
            print('name: {}\nvalue: {}\npath: {}'.format(name, value, path))
            with open(path) as f:
                d = json.load(f)
            d['arguments'][name] = value
            pprint(d)
            with open(path, 'w') as f:
                json.dump(d, f, indent=2, sort_keys=True)
        # Run
        log = '_'.join(['log', prefix])
        logs.append(os.path.abspath(log))
        if not is_test:
            with open(log, 'w+') as f:
                tokens = shlex.split(run_cmd)
                cmd = ['python']
                # cmd = ['nohup', 'python']  # used with preexec_fn=os.setpgrp
                cmd.extend(tokens)
                print(cmd)
                # preexec_fn=os.setpgrp is for nohup correct work
                # bufsize=-1 system ruled (for performance increase)
                process = Popen(cmd, stdout=f, stderr=f, bufsize=-1)
                # process = Popen(cmd, stdout=f, stderr=f, preexec_fn=os.setpgrp)
                pids.append(process.pid)
                processes.add(process)
        else:
            with open(log, 'w+') as f:
                pass
            pids.append(c_i + 1)
        print('PID: {}'.format(pids[-1]))
        print('log: {}'.format(logs[-1]))
        os.chdir(os.path.join('..', '..'))
    print('Number of processes: {}'.format(len(pids)))
    dirname = os.path.join(prefix)
    os.chdir(dirname)
    ps_filename = 'ps.json'
    print('Processes file: {}'.format(os.path.abspath(ps_filename)))
    ps_data = dict()
    for c_i, p in enumerate(pids):
        d = dict()
        d['log_path'] = os.path.abspath(logs[c_i])
        ps_data[p] = d
    print('Processes data:')
    pprint(ps_data)
    if not is_test:
        with open(ps_filename, 'w+') as f:
            json.dump(ps_data, f, indent=2, sort_keys=True)
    os.chdir(os.path.join('..'))
    if cmd_args.wait:  # Wait for end of all subprocesses
        print('Waiting')
        for p in processes:
            result = p.wait()
            print('pid: {}, result: {}'.format(p.pid, result))
    print('End')
