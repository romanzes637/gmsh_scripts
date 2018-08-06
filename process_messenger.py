import argparse
import json
import os
import shlex
from subprocess import Popen


class ProcessMessenger:
    def __init__(self, processes, emails, n_log_lines, is_full_log):
        """
        Class for messaging when processes are done.
        :param processes: 2D dict (pid: ('status': 1 or 0, 'log_path': absolute path))
        :param emails: list of string emails [bla@bla.bla, ...]
        :param n_log_lines: int number of lines from log's end to email
        :param is_full_log: bool If True then attach full log to email (Warning: Log may be too large)
        """
        self.processes = processes
        self.emails = emails
        self.n_log_lines = n_log_lines
        self.is_full_log = is_full_log

    def check_processes(self):
        for pid, data in self.processes.items():
            if data['status'] != 0:
                try:
                    os.kill(int(pid), 0)  # Check process running
                except OSError:
                    print('Done {}'.format(pid))
                    self.processes[pid]['status'] = 0
                    self.send_email(pid)
                else:
                    pass

    def send_email(self, pid):
        print('Sending mail')
        log_path = self.processes[pid]['log_path']
        body = 'log_path:{}'.format(log_path)
        subject = 'Done:{}'.format(pid)
        if log_path is not None:
            abs_log_path = os.path.expanduser(log_path)
            if not self.is_full_log:
                temp_log_path = os.path.abspath('temp_log_{}.txt'.format(pid))
                lines = list()
                with open(abs_log_path) as f:
                    for i, line in enumerate(reversed(f.readlines())):
                        if i < self.n_log_lines:
                            lines.append(line)
                temp_log = str().join(lines)
                with open(temp_log_path, 'w+') as af:
                    af.write(temp_log)
                attachment = temp_log_path
            else:
                attachment = abs_log_path
            for e in self.emails:
                recipient = e
                print(recipient)
                command = "ssh ibrae-master echo {} | mail -s {} -a {} {}".format(
                    body, subject, attachment, recipient)
                split_command = shlex.split(command)
                # print(split_command)
                process = Popen(split_command)
                process.wait()
        else:
            for e in self.emails:
                recipient = e
                print(recipient)
                command = "ssh ibrae-master echo {} | mail -s {} {}".format(
                    body, subject, recipient)
                split_command = shlex.split(command)
                # print(split_command)
                process = Popen(split_command)
                process.wait()
        if log_path is not None and not self.is_full_log:
            os.remove(temp_log_path)
        print('Done sending mail')


def main():
    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input')
    parser.add_argument('-m', '--emails', nargs='+', help='recipients emails')
    parser.add_argument('-n', '--n_log_lines', help='number of log lines', default=10)
    parser.add_argument('-v', '--attach_full_log', help='attach full log ', action='store_true')
    args = parser.parse_args()
    print(args)
    # Get input
    with open(args.input) as f:
        ps = json.load(f)
    print(ps)
    # Init ProcessMessenger
    pm = ProcessMessenger(ps, args.emails, args.n_log_lines, args.attach_full_log)
    all_done = False
    print('Start monitoring')
    while not all_done:  # Stop if all processes done
        # Update processes statuses
        pm.check_processes()
        # Update input file
        with open(args.input, 'w') as f:
            json.dump(pm.processes, f, indent=2, sort_keys=True)
        # Stop if all processes done
        all_done = True
        for process, data in pm.processes.items():
            if data['status'] == 1:
                all_done = False
                break
    print('End monitoring')

if __name__ == '__main__':
    main()
