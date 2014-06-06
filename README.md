# Instance tracker

With the Instance Tracker package you'll be able to easily track and manage the various instances of your application, as well as analizing interesting statistical information.

## Installation

To install this package, first of all head to your code directory and clone this repository:

```sh
git clone https://github.com/tommy39/instance-tracker.git
cd instance-tracker
```

Then you can either install the package in a dedicated virtual environment (suggested):

```sh
virtualenv env
. env/bin/activate
pip install -r requirements.txt
```

or you can directly install it for the current user by running this command:

```sh
python setup.py install
```

## Configuration

After you installed the package, you should create your own settings file

```sh
cp tracker/settings.cfg.example tracker/settings.cfg
```

and personalize it.

Keep in mind that `settings.cfg` has to be written following a correct Python syntax.

### Secret key

The first thing to do is to fill the `SECRET_KEY` field.

Just add whichever key you prefer or insert a random alphanumeric string.

### Timezone and time format

The fields `BABEL_DEFAULT_TIMEZONE` and `BABEL_DEFAULT_LOCALE` determine, respectively, the in which timezone the times will be shown and in which format.

The default values are `UTC` for the timezone and `en_GB` (i.e. English format) for the time format.

### Application name

To personalize your Instance Tracker application you should change the field `APP_NAME` to your application name.

### Crawling endpoints

To allow your Instance Tracker to crawl additional information from the servers running your application, you should specify all the necessary endpoints in the `CRAWLING_ENDPOINTS` field.

This field is going to be a Python list where each element is a Python dictionary containing an `url` and (optionally) a `headers` dictionary. Each endpoint url will be appended to the server base url at the moment of sending the http request to crawl the information.

### Crawled fields

All the configurations relative to the crawled fields are managed through the `CRAWLED_FIELDS_SETTINGS` field, which is going to be a dictionary of dictionaries.

Each field must have a key name equals to the corresponding crawled field name. Any mismatching field will be ignored.

For each field, the following parameters can be specified:

- **label:** a string that specifies how the field name will be rendered across the Instance Tracker. The default value is the field name with spaces instead of underscores and with the first word starting with a capital letter;
- **chart:** a boolean value that indicates whether to include or not that field amongst the statistics. Default: `False`;
- **chart_type:** if `chart` is set to `True` it specifies with which kind of chart the field statistics will be displayed. Accepted values are: `'bar'`, for a barchart, `'line'`, for a linechart, and `'pie'`, for a piechart. Default: `'bar'`;
- **aggregation:** if the field cannot be directly shown (for example it's a list or a dictionary) you have to define an aggregation function to aggregate the values inside the field and use the aggregated value instead. At the moment, only numeric values are supported and the accepted aggregation functions are: `None`, when no aggregation is necessary, `'sum'`, to aggregate by sum, and `'avg'`, to aggregate by average. Default: `None`;
- **chart_aggregation:** similar to `aggregation`, it specifies an aggregation function that will be used in the statistics chart, if `chart` is set to `True`. Accepted values are: `'count'`, to show the number of instances per each category, `'sum'` and `'avg'`. Default: `'count'`;
- **chart_aggregate_by:** a string that specifies by which (other) field the current field should be aggregated in the statistics chart. It can be any of the other crawled fields or `'country'`. Be wary that if `chart_aggregation` is set to `'count'` this field will be ignored. Default: `'country'`.

### Celery periodic task

To specify the time interval between each periodic crawl, you should modify the `CELERYBEAT_SCHEDULE` field.

## API implementation

To allow your application, and therefore each instance running it, to communicate with your Instance Tracker you have to use the three APIs available:

- **Create instance:** this API is used to create a new instance record in the Instance Tracker DB.
    - *Endpoint:* `/instance/`;
    - *Request type:* `POST`;
    - *Data:* the url of the instance server, the contact person name and e-mail address and the organisation name;
    - *Response:* the instance UUID.
- **Update instance:** used to update the instance record in the Instance Tracker DB whenever some field is changed in the instance server. Also used when the Instance Tracking has to be be enabled/disabled for that instance.
    - *Endpoint*: `/instance/<uuid>`;
    - *Request type:* `PATCH`;
    - *Data:* every combination of the following fields: server url, contact person name, contact e-mail address and enabled status (`True` or `False`);
    - *Response:* a summary of the instance main information in json format.
- **Get instance:** used to retrieve the main information of a certain instance.
    - *Endpoint:* `/instance/uuid`;
    - *Request type:* `GET`;
    - *Data:* none;
    - *Response:* a summary of the instance main information in json format (like for the update API).

## Usage

The Instance Tracker is basically composed by two main functionalities: instance details & management and statistics.

For others more advanced functionalities a python script, `manage.py`, has been written and included in the package.

### Instance details & management

The Instance Tracker allows you to view a comprehensive list of all the instances in the DB, with the possibility to filter them by a few criteria. Also in the server list you can sort the instances selected by one of the available fields (be it one of the main fields or one of the crawled fields) and you can choose to run at any moment the crawler to crawl all the instances.

By clicking on the detail button for a specific instance, you'll be able to explore it's main and crawled information and see a map with the approximated physical location of the server.

### Statistics

In the statistics page you'll see the country distribution by default, i.e. the position on the map of the servers in the DB and the percentage of servers for each country.

On top of that, it will also be displayed all the additional charts you might have configured in the settings file.

### manage.py

For more advanced operations you'll have to use the script manage.py.

To use the script run

```sh
manage_tracker <arguments>
```

if you installed the tracker with `setup.py`, or

```sh
python manage.py <arguments>
```

otherwise.

The available arguments and possibile operations are the following:

- **db drop:** drops all the DB tables;
- **db create:** creates the DB tables;
- **db recreate:** drops all DB tables and creates new tables (same as *drop* and then *create*);
- **crawl [uuid]:** crawl a specific instance (if *uuid* is passed) or all the active instances;
- **create_usr usr pswd:** creates a new user with *usr*:*pswd* as credentials;
- **runworker [concurrency]:** runs a celery worker.
