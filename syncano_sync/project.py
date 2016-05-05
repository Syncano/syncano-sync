# coding=UTF8
import json
import os
import time

import yaml

from . import LOG
from .classes import pull_classes, push_classes, validate_classes
from .scripts import pull_scripts, push_scripts, validate_scripts


class Project(object):
    def __init__(self, classes=None, scripts=None, timestamp=None, **kwargs):
        self.classes = classes or {}
        self.scripts = scripts or []
        self.timestamp = timestamp or time.time()

    @classmethod
    def from_config(cls, config):
        with open(config, 'rb') as fp:
            cfg = yaml.safe_load(fp)
        cfg['timestamp'] = os.path.getmtime(config)
        project = cls(**cfg)
        project.validate()
        return project

    def write(self, config):
        with open(config, 'wb') as fp:
            fp.write(yaml.safe_dump({
                'classes': self.classes,
                'scripts': self.scripts
            }, default_flow_style=False))

    def write_json(self, config):
        with open(config, 'wb') as fp:
            json.dump({
                'classes': self.classes,
                'scripts': self.scripts
            }, fp, indent=2)

    def update_from_instance(self, instance):
        """Updates project data from instances"""
        self.classes = pull_classes(instance, self.classes.keys())
        self.scripts = pull_scripts(instance,
                                    set(s['label'] for s in self.scripts))

    @classmethod
    def pull_from_instance(cls, instance, scripts=None, classes=None):
        LOG.info("Pulling instance data from syncano")
        classes = pull_classes(instance, classes or [])
        scripts = pull_scripts(instance, scripts or [])
        LOG.info("Finished pulling instance data from syncano")
        return cls(classes, scripts)

    def push_to_instance(self, instance, scripts=None, classes=None):
        try:
            last_sync = os.path.getmtime('.sync')
        except OSError:
            with open('.sync', 'wb'):  # touch file
                pass
            last_sync = 0
        scripts = []
        for script in self.scripts:
            if os.path.getmtime(script['script']) > last_sync:
                scripts.append(script)

        if scripts:
            push_scripts(instance, scripts)
        if self.timestamp > last_sync:
            push_classes(instance, self.classes)
        elif not scripts:
            LOG.info('Nothing to sync.')
        now = time.time()
        os.utime('.sync', (now, now))

    def validate(self):
        validate_classes(self.classes)
        validate_scripts(self.scripts)
