from flask import current_app


def pretty_name(value):
    return current_app.config['EXTRA_FIELD_LABELS'].get(value, (value[0].upper() + value[1:]).replace('_', ' '))
