# coding=UTF8
from __future__ import unicode_literals
from __future__ import print_function

import re
import os


RUNTIME_EXTENSION = (
    (re.compile('golang'), '.go'),
    (re.compile('nodejs.*'), '.js'),
    (re.compile('php'), '.php'),
    (re.compile('python.*'), '.py'),
    (re.compile('ruby'), '.rb'),
    (re.compile('swift'), '.swift')
)


def get_runtime_extension(runtime):
    for regexp, ext in RUNTIME_EXTENSION:
        if regexp.match(runtime):
            return ext
    raise ValueError('Runtime name "%s" not recognized' % runtime)


def pull_scripts(instance, include):
    """
    Pull scripts from instance and store them in scripts directory.
    If scripts is empty list all scripts are pulled, otherwise script
    label has to be in a list. Script labels are changed to be compatibile with
    file names. All whitespaces, slashes and backslashes are replaced with '_'.
    """
    seen_names = {}
    if not os.path.exists('scripts'):
        os.makedirs('scripts')

    pulled = []
    for script in instance.scripts.all():

        if include and script.label not in include:
            continue

        ext = get_runtime_extension(script.runtime_name)
        filename = re.sub(r'[\s/\\]', '_', script.label) + ext

        if filename in seen_names:
            print("Script {0.label}({0.id}) label clashes with"
                  "script {1.label}({1.id}). Skipping."
                  .format(script, seen_names[filename]))
            continue

        path = os.path.join('scripts', filename)

        with open(path, 'wb') as script_file:
            script_file.write(script.source)

        pulled.append({
            'label': script.label.encode('utf8'),
            'script': path.encode('utf8'),
            'runtime': script.runtime_name.encode('utf8')
        })
    return pulled
