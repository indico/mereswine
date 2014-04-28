from ..core import db


class Instance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: add columns

    def __repr__(self):
        # TODO: show more useful columns to identify the object, e.g. the URL
        return '<Instance {}>'.format(self.id)
