# coding=UTF8
from __future__ import unicode_literals
from __future__ import print_function

def field_schema_to_str(schema):
    out = schema['type']
    if schema['type'] == 'reference' and schema['target']:
        out += ' ' + schema['target']
    if schema.get('filter_index', False):
        out += " filtered"
    if schema.get('order_index', False):
        out += " ordered"
    return out

def pull_classes(instance, include):
    out = {}
    for cls in instance.classes.all():
        if include and cls.name not in include:
            continue
        out[cls.name] = dict(
            group_permissions=cls.group_permissions,
            other_permissions=cls.other_permissions,
            fields={f['name']: str(field_schema_to_str(f)) for f in cls.schema}
        )
    return out
