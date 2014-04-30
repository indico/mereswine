from ..core import db


class Instance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True, nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    url = db.Column(db.String, nullable=False)
    contact = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    organisation = db.Column(db.String, nullable=False)
    crawl_date = db.Column(db.DateTime)
    crawled_data = db.Column(db.Text)

    def __repr__(self):
        return '<Instance {0} {1}>'.format(self.id, self.url)

    def __json__(self):
        return {'uuid': self.uuid,
                'enabled': self.enabled,
                'url': self.url,
                'contact': self.contact,
                'email': self.email,
                'organisation': self.organisation}
