
import os
import re
import sys
import subprocess

import yaml


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


def install():
    if not os.path.exists('env'):
        # Make virtualenv.
        try:
            subprocess.check_call(['virtualenv', 'env'])
            Logger.info('Virtualenv OK')
        except:
            Logger.error('Virtualenv Error')
            sys.exit(1)

    # Virtualenv already exists.
    Logger.info('Virtualenv OK')

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


def start(mode):
    if mode == 'router':
        subprocess.Popen(['setsid', 'env/bin/python', 'rap_router.py'])
        Logger.info('RAP Router Running')
    elif mode == 'in':
        subprocess.Popen(['setsid', 'env/bin/python', 'rap_server.py', 'in'])
        Logger.info('RAP IN Server Running')
    elif mode == 'out':
        subprocess.Popen(['setsid', 'env/bin/python', 'rap_server.py', 'out'])
        Logger.info('RAP OUT Server Running')


def stop():
    # Sample output of `ps -ef`
    # UID        PID  PPID  C STIME TTY          TIME CMD
    # root      3410     1  0 12:57 ?        00:00:00 env/bin/python rap_router.py
    # root      3416  3378  0 12:57 pts/2    00:00:00 grep --color=auto rap
    output = subprocess.check_output(['ps', '-ef'])
    for line in output.splitlines():
        if 'rap_router.py' in line or 'rap_server.py' in line:
            pid = int(line.split()[1])
            os.kill(pid, signal.SIGKILL)
    Logger.info('RAP Stoped at ' + host)


def restart():
    stop()
    start()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['install', 'start-in', 'start-out', 'start-router', 'stop']:
        Logger.warning('Usage: rap_ctrl.py install|start-in|start-out|start-router|stop')
        sys.exit(1)

    # Change work directory to the rap root. That is the directory containing
    # rap_ctrl.py. Then this script can be executed anywhere.
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    if sys.argv[1] == 'install':
        install()
    elif sys.argv[1] == 'start-in':
        start('in')
    elif sys.argv[1] == 'start-out':
        start('out')
    elif sys.argv[1] == 'start-router':
        start('router')
    elif sys.argv[1] == 'stop':
        stop()


if __name__ == '__main__':
    main()
