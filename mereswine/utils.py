from __future__ import division

import os
import sys
from collections import Counter

import pkg_resources
from flask import current_app
from flask.helpers import get_root_path
from flask_mail import Message


def package_is_editable(package):
    """Check whether the Python package is installed in 'editable' mode"""
    # based on pip.dist_is_editable
    dist = pkg_resources.get_distribution(package)
    for path_item in sys.path:
        egg_link = os.path.join(path_item, dist.project_name + '.egg-link')
        if os.path.isfile(egg_link):
            return True
    return False


def get_config_path():
    # env var has priority
    try:
        return os.path.expanduser(os.environ['MERESWINE_CONFIG'])
    except KeyError:
        pass
    # try finding the config in various common paths
    paths = [os.path.expanduser('~/.mereswine.cfg'), '/etc/mereswine.cfg']
    # If it's an editable setup (ie usually a dev instance) allow having
    # the config in the package's root path
    if package_is_editable('mereswine'):
        paths.insert(0, os.path.normpath(os.path.join(get_root_path('mereswine'), 'mereswine.cfg')))
    for path in paths:
        if os.path.exists(path):
            return path
    raise Exception('No mereswine config found. Point the MERESWINE_CONFIG env var to your config file or '
                    'move/symlink the config in one of the following locations: {}'.format(', '.join(paths)))


def pretty_name(value):
    try:
        return current_app.config['CRAWLED_FIELDS_SETTINGS'][value]['label']
    except KeyError:
        return (value[0].upper() + value[1:]).replace('_', ' ')


def aggregate(values, aggregation_func):
    if hasattr(values, 'values'):
        values = values.values()

    if aggregation_func is None:
        return values
    elif aggregation_func == 'count':
        return Counter(values).most_common()
    elif aggregation_func == 'sum':
        return sum(values)
    elif aggregation_func == 'avg':
        return sum(values) / len(values)
    elif aggregation_func == 'min':
        return min(values)
    elif aggregation_func == 'max':
        return max(values)
    else:
        raise ValueError('Invalid aggregation function: {0}'.format(aggregation_func))


def aggregate_values(instance, extra_fields):
    crawled_fields_settings = current_app.config['CRAWLED_FIELDS_SETTINGS']
    aggregated_fields = []

    for field in extra_fields:
        try:
            aggregation_func = crawled_fields_settings[field]['aggregation']
        except KeyError:
            aggregation_func = None

        if instance.crawled_data is not None and instance.crawled_data.get(field, None) is not None:
            aggregated_fields.append({
                'field': field,
                'value': aggregate(instance.crawled_data[field], aggregation_func)
            })
        else:
            aggregated_fields.append({
                'field': field,
                'value': 'Unknown'
            })

    return aggregated_fields


def aggregate_chart(extended_instances, extra_fields):
    crawled_fields_settings = current_app.config['CRAWLED_FIELDS_SETTINGS']
    aggregated_fields = {}

    for field in extra_fields:
        if not crawled_fields_settings.get(field, {}).get('chart', False):
            continue

        try:
            aggregation_func = crawled_fields_settings[field]['chart_aggregation']
        except KeyError:
            aggregation_func = 'count'
        try:
            chart_aggregate_by = crawled_fields_settings[field]['chart_aggregate_by']
        except KeyError:
            chart_aggregate_by = 'country'
        try:
            chart_type = crawled_fields_settings[field]['chart_type']
        except KeyError:
            chart_type = 'bar'
        if chart_type == 'pie' and aggregation_func == 'avg':
            aggregation_func = 'sum'

        values = []
        values_groups = {}
        for instance in extended_instances:
            if aggregation_func == 'count':
                value = next((instance_field['value'] for instance_field in instance['fields']
                              if instance_field['field'] == field), None)
                values.append(value)
            else:
                value = next((instance_field['value'] for instance_field in instance['fields']
                              if instance_field['field'] == field), None)
                if value == 'Unknown':
                    continue

                if chart_aggregate_by == 'country':
                    if instance['instance'].geolocation:
                        category = instance['instance'].geolocation['country_name']
                    else:
                        category = 'Unknown'
                else:
                    category = instance['instance'].crawled_data.get(chart_aggregate_by, 'Unknown')

                try:
                    values_groups[category].append(value)
                except KeyError:
                    values_groups[category] = [value]

        if aggregation_func == 'count':
            values = aggregate(values, aggregation_func)
            aggregation_label = '# of instances'
            aggregate_by_label = pretty_name(field)
        else:
            for group in values_groups:
                values.append((group, aggregate(values_groups[group], aggregation_func)))
            aggregation_label = aggregation_func
            aggregate_by_label = pretty_name(chart_aggregate_by)

        if values:
            aggregated_fields[field] = {
                'data': values,
                'aggregation_label': aggregation_label,
                'aggregate_by_label': aggregate_by_label,
                'chart_type': chart_type
            }

    return aggregated_fields


def send_email(subject, body):
    from mereswine.core import mail
    subject = "[{}] {}".format(current_app.config['APP_NAME'], subject)
    msg = Message(subject,
                  sender=current_app.config['MAIL_SENDER'],
                  recipients=[current_app.config['MAIL_RECIPIENT']])

    msg.body = body
    mail.send(msg)
