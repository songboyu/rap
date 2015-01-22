#!/usr/bin/python
"""Control script.

@author: sniper
@since: 2015-1-19
"""

import os
import sys
import signal
import argparse
import subprocess


class Logger:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def info(msg):
        print '[' + __file__ + '] ' + Logger.OKGREEN + msg + Logger.ENDC

    @staticmethod
    def warning(msg):
        print '[' + __file__ + '] ' + Logger.WARNING + msg + Logger.ENDC

    @staticmethod
    def error(msg):
        print '[' + __file__ + '] ' + Logger.FAIL + msg + Logger.ENDC


def install(args):
    try:
        # Make virtualenv.
        subprocess.check_call(['virtualenv', 'env'])
        Logger.info('Virtualenv OK')
    except:
        Logger.error('Virtualenv Error')
        sys.exit(1)

    try:
        # Install required python packages via pip.
        subprocess.check_call(['env/bin/pip', 'install', '-r', 'requirements.txt'])
        Logger.info('PIP Install OK')
    except:
        Logger.error('PIP Install Error')
        sys.exit(1)

    if not os.path.exists('log'):
        os.mkdir('log')

    # Everything ok.
    Logger.info('Install OK')


def start(args):
    if args.router:
        subprocess.Popen(['setsid', 'env/bin/python', 'rap_router.py'])
        Logger.info('RAP Router Running')
    elif args._out:
        for i in range(args.number):
            subprocess.Popen(['setsid', 'env/bin/python', 'rap_server.py', 'out'])
            if args.verbose:
                Logger.info('RAP OUT Server Running ' + str(i))
        Logger.info('%d RAP OUT Server Running' % args.number)
    else:
        # args.in
        for i in range(args.number):
            subprocess.Popen(['setsid', 'env/bin/python', 'rap_server.py', 'in'])
            if args.verbose:
                Logger.info('RAP IN Server Running ' + str(i))
        Logger.info('%d RAP IN Server Running' % args.number)


def stop(args):
    # Sample output of `ps -ef`
    # UID        PID  PPID  C STIME TTY          TIME CMD
    # root      3410     1  0 12:57 ?        00:00:00 env/bin/python rap_router.py
    # root      3416  3378  0 12:57 pts/2    00:00:00 grep --color=auto rap
    output = subprocess.check_output(['ps', '-ef'])
    for line in output.splitlines():
        if args.router:
            kill = 'rap_router.py' in line
        elif args._out:
            kill = 'rap_server.py out' in line
        elif args._in:
            kill = 'rap_server.py in' in line
        else:
            # Kill all
            kill = 'rap_router.py' in line or 'rap_server.py' in line

        if kill:
            pid = int(line.split()[1])
            os.kill(pid, signal.SIGKILL)
            if args.verbose:
                Logger.info(' '.join(line.split()[7:]) + ' Stoped')
    Logger.info('RAP Stoped')


def show(args):
    output = subprocess.check_output(['ps', '-ef'])
    for line in output.splitlines():
        if ('rap_router.py' in line or 'rap_server.py' in line) and 'grep' not in line:
            print line


def main(): 

    parser = argparse.ArgumentParser()
    # Action and the concurrent limit.
    parser.add_argument('action', choices=['install', 'start', 'stop', 'show'])
    parser.add_argument('-n', '--number', type=int, default=8, help='start rap server in n processes')
    # Start mode.
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--router', action='store_true', help='start or stop rap router')
    group.add_argument('-i', '--in', dest='_in', action='store_true', help='start or stop rap server in IN mode.')
    group.add_argument('-o', '--out', dest='_out', action='store_true', help='start or stop rap server in OUT mode.')
    # Extra flags.
    parser.add_argument('-v', '--verbose', action='store_true', help='turn verbose mode on')
    args = parser.parse_args()

    # Change work directory to the rap root. That is the directory containing
    # rap_ctrl.py. Then this script can be executed anywhere.
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Dispatch
    if args.action == 'install':
        install(args)
    elif args.action == 'start':
        start(args)
    elif args.action == 'stop':
        stop(args)
    elif args.action == 'show':
        show(args)


if __name__ == '__main__':
    main()
