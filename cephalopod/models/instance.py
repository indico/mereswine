import json
from sqlalchemy.types import TypeDecorator, VARCHAR

from ..core import db


class JSONEncodedDict(TypeDecorator):
    """
        Represents an immutable structure as a json-encoded string.
        Usage::
            JSONEncodedDict(255)
    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class Instance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    url = db.Column(db.String, nullable=False)
    contact = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    organization = db.Column(db.String, nullable=False)
    crawl_date = db.Column(db.DateTime)
    crawled_data = db.Column(JSONEncodedDict)
    geolocation = db.Column(JSONEncodedDict)
    registration_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Instance {0} {1}>'.format(self.id, self.url)

    def __json__(self):
        return {'uuid': self.uuid,
                'enabled': self.enabled,
                'url': self.url,
                'contact': self.contact,
                'email': self.email,
                'organization': self.organization,
                'registered': self.registration_date}
