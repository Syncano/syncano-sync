# coding=UTF8
import yaml

from .scripts import pull_scripts
from .classes import pull_classes


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
            }))

    @classmethod
    def pull_from_instance(cls, instance, scripts=None, classes=None):
        classes = pull_classes(instance, classes or [])
        scripts = pull_scripts(instance, scripts or [])
        return cls(classes, scripts)
