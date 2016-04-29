# coding=UTF8
from __future__ import unicode_literals
from __future__ import print_function

from ConfigParser import ConfigParser
import argparse
import os
from getpass import getpass

import syncano
from syncano.exceptions import SyncanoException

from .project import Project

ACCOUNT_KEY = ''

ACCOUNT_CONFIG = ConfigParser()

COMMANDS = {}


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
        ACCOUNT_CONFIG.set('DEFAULT', 'key', ACCOUNT_KEY)
        with open(args.config, 'wb') as fp:
            ACCOUNT_CONFIG.write(fp)
    except SyncanoException as error:
        print(error)


@command
@argument('-s', '--script', action='append', nargs='*', dest='scripts',
          help="Pull only this script from syncano")
@argument('-c', '--class', action='append', nargs='*', dest='classes',
          help="Pull only this class from syncano")
@argument('-a', '--all', action='store_true',
          help="Force push all configuration")
@argument('instance', help="Destination instance name")
def push(args):
    """
    Push configuration changes to syncano.
    """
    print("push", args)


@command
@argument('instance', help="Source instance name")
@argument('script', help="script label or script name")
def run(args):
    """Execute script on syncano."""
    pass


@command
@argument('-s', '--script', action='append', nargs='*', dest='scripts',
          help="Pull only this script from syncano")
@argument('-c', '--class', action='append', nargs='*', dest='classes',
          help="Pull only this class from syncano")
@argument('instance', help="Source instance name")
def pull(args):
    """
    Pull configuration from syncano and store it in current directory.
    Updates syncano.yml configuration file, and places scripts in scripts
    directory.
    """
    con = syncano.connect(api_key=args.key)
    instance = con.instances.get(name=args.instance)
    Project.pull_from_instance(instance).write(args.file)


def main():
    ACCOUNT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.syncano')

    parser = argparse.ArgumentParser(
        description='Syncano synchronization tool.'
    )
    parser.add_argument('--file', '-f', default='syncano.yml',
                        help='Instance configuraion file.')
    parser.add_argument('--config', default=ACCOUNT_CONFIG_PATH,
                        help='Account configuration file.')
    parser.add_argument('--key', default=os.environ.get('SYNCANO_API_KEY', ''),
                        help='override ACCOUNT_KEY used for authentication.')

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands'
    )

    for fname, func in COMMANDS.iteritems():
        subparser = subparsers.add_parser(fname, description=func.__doc__)
        for args, kwargs in getattr(func, 'arguments', []):
            subparser.add_argument(*args, **kwargs)
        subparser.set_defaults(func=func)
    namespace = parser.parse_args()

    read = ACCOUNT_CONFIG.read(namespace.config)
    if read and not namespace.key:
        namespace.key = ACCOUNT_CONFIG.get('DEFAULT', 'key')

    namespace.func(namespace)

if __name__ == "__main__":
    main()
