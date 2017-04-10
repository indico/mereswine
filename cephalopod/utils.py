from __future__ import division

from collections import Counter
from flask import current_app, redirect, session, url_for
from functools import wraps


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


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('.login'))
        return f(*args, **kwargs)
    return decorated_function
