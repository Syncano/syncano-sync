# coding=UTF8
import json
import logging
import yaml

from .scripts import pull_scripts
from .classes import pull_classes


LOG = logging.getLogger(__name__)


class Project(object):
    def __init__(self, classes=None, scripts=None, **kwargs):
        self.classes = classes or {}
        self.scripts = scripts or []

    @classmethod
    def from_config(cls, config):
        with open(config, 'rb') as fp:
            cfg = yaml.safe_load(fp)
        return cls(**cfg)

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

    @classmethod
    def pull_from_instance(cls, instance, scripts=None, classes=None):
        LOG.info("Pulling instance data from syncano")
        classes = pull_classes(instance, classes or [])
        scripts = pull_scripts(instance, scripts or [])
        LOG.info("Finished pulling instance data from syncano")
        return cls(classes, scripts)

    def push_to_instance(self, instance, scripts=None, classes=None):
        pass
