# coding=UTF8
from ConfigParser import ConfigParser
import argparse
import os
from getpass import getpass

import syncano
from syncano.exceptions import SyncanoException

ACCOUNT_KEY = ''

CONFIG = ConfigParser()

COMMANDS = {}


def _parse_config():
    pass


def command(func):
    COMMANDS[func.func_name] = func
    return func


def argument(*args, **kwargs):
    def wrapper(f):
        if not hasattr(f, 'arguments'):
            f.arguments = []
        f.arguments.append((args, kwargs))
        return f
    return wrapper


@command
def login(args):
    """
    Log in to syncano using email and password and store ACCOUNT_KEY
    in configuration file.
    """
    email = os.environ.get('SYNCANO_EMAIL', None)
    if email is None:
        email = raw_input("email: ")
    password = os.environ.get('SYNCANO_PASSWORD', None)
    if password is None:
        password = getpass("password: ").strip()
    connection = syncano.connect().connection()
    try:
        ACCOUNT_KEY = connection.authenticate(email=email, password=password)
        CONFIG.set('syncano', 'account_key', ACCOUNT_KEY)
        CONFIG.write(args.config)
    except SyncanoException as error:
        print error


@command
@argument('-s', '--script', action='append', nargs='*', dest='scripts',
          help="Pull only this script from syncano")
@argument('-c', '--class', action='append', nargs='*', dest='classes',
          help="Pull only this class from syncano")
@argument('instance', help="Destination instance name")
def push(args):
    """
    Push configuration changes to syncano.
    """
    print "push", args


@command
@argument('-s', '--script', action='append', nargs='*', dest='scripts',
          help="Pull only this script from syncano")
@argument('-c', '--class', action='append', nargs='*', dest='classes',
          help="Pull only this class from syncano")
@argument('instance', help="Source instance name")
def pull(args):
    """
    Pull configuration from syncano and store it in current directory.
    Generates syncano.yml configuration file, and places scripts in scripts
    directory.
    """
    print "pull", args


@command
def help(args):
    args.parser


def main():
    parser = argparse.ArgumentParser(
        description='Syncano synchronization tool.')
    CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.syncano')
    parser.add_argument('--config', default=CONFIG_PATH)
    parser.add_argument('--key', default=os.environ.get('SYNCANO_API_KEY', ''))
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands')
    for fname, func in COMMANDS.iteritems():
        subparser = subparsers.add_parser(fname, description=func.__doc__)
        for args, kwargs in getattr(func, 'arguments', []):
            subparser.add_argument(*args, **kwargs)
        subparser.set_defaults(func=func)
    namespace = parser.parse_args()

    CONFIG.read(namespace.config)

    namespace.func(namespace)

if __name__ == "__main__":
    main()
