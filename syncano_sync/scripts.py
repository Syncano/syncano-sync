# coding=UTF8
from __future__ import print_function, unicode_literals

import os
import re
from collections import defaultdict

from syncano.models import fields
from syncano.models.incentives import Script

from . import LOG, mute_log


ALLOWED_RUNTIMES = {
    'golang': '.go',
    'nodejs': '.js',
    'nodejs_library_v0.4': '.js',
    'nodejs_library_v1.0': '.js',
    'php': '.php',
    'python': '.py',
    'python_library_v4.2': '.py',
    'python_library_v5.0': '.py',
    'ruby': '.rb',
    'swift': '.swift',
}


Script.runtime_name = fields.StringField()


def get_runtime_extension(runtime):
    try:
        return ALLOWED_RUNTIMES[runtime]
    except KeyError:
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
        LOG.debug("Creating scripts directory")
        os.makedirs('scripts')

    pulled = []
    for script in instance.scripts.all():

        if include and script.label not in include:
            continue

        ext = get_runtime_extension(script.runtime_name)
        filename = re.sub(r'[\s/\\]', '_', script.label)

        if not filename.endswith(ext):
            filename += ext

        if filename != script.label:
            LOG.warn('Saving script "{0}" as "{1}"'.format(script.label,
                                                           filename))

        if filename in seen_names:
            LOG.warn("Script {0.label}({0.id}) label clashes with"
                     "script {1.label}({1.id}). Skipping."
                     .format(script, seen_names[filename]))
            continue

        path = os.path.join('scripts', filename)

        with open(path, 'wb') as script_file:
            script_file.write(script.source)

        script_info = {
            'label': script.label.encode('utf8'),
            'script': path.encode('utf8'),
            'runtime': script.runtime_name.encode('utf8')
        }

        if script.config:
            script_info['config'] = script.config

        pulled.append(script_info)
    return pulled


def push_scripts(instance, scripts):
    """
    Push selected scripts to instance.
        - instance - instance object to push scripts to
        - scripts - a list of dictionaries containing configurations for
                    scripts
    """
    LOG.debug('Pushing scripts')
    LOG.debug('Pulling remote scripts')
    remote_scripts_mapping = defaultdict(list)
    for remote_script in instance.scripts.all():
        remote_scripts_mapping[remote_script.label].append(remote_script)

    LOG.debug('Pushing local scripts')
    for s in scripts:
        if s['label'] in remote_scripts_mapping:
            remote_count = len(remote_scripts_mapping[s['label']])
            if remote_count > 1:
                LOG.error('You have {0} scripts with label {1} on'
                          'syncano. Skipping'.format(remote_count, s['label']))
                continue
            remote_script = remote_scripts_mapping[s['label']][0]
        else:
            remote_script = instance.scripts.model(
                label=s['label'],
                runtime_name=s['runtime'],
                instance_name=instance.name,
                config={}
            )
        with open(s['script'], 'rb') as source:
            remote_script.source = source.read()

        # FIXME: Waiting for python library fix.
        config = s.get('config', {})
        remote_script.config.update(config)

        LOG.debug('Pushing script {label}'.format(**s))
        with mute_log():
            remote_script.save()


def validate_script(script):
    if not script.get('label'):
        raise ValueError('You have to provide script label.')

    source = script.get('script')
    if source is None:
        raise ValueError('You have to provide script source for script '
                         '"{label}"'.format(**script))

    if not os.path.exists(source):
        raise ValueError(
            'Could not find script "{source}" file'.format(**script)
        )

    runtime = script.get('runtime')
    if not runtime:
        ext = os.path.splitext(source)[1]
        LOG.warning(
            'Runtime for script {label} not provided. Guessing runtime basing'
            'on file extension'.format(**script)
        )

        for k, v in ALLOWED_RUNTIMES.iteritems():
            if v == ext:
                script['runtime'] = runtime = k
                LOG.warning(
                    'Using runtime {runtime} for script {label}'.format(
                        **script
                    )
                )
                break

    if runtime not in ALLOWED_RUNTIMES:
        raise ValueError('Runtime "{runtime}" defined for script "{label}"'
                         'is not supported'.format(**script))


def validate_scripts(scripts):
    for s in scripts:
        validate_script(s)
