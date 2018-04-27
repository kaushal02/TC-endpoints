from mongoengine import EmbeddedDocument, StringField, FloatField
from collections import OrderedDict

class Gender(EmbeddedDocument):
    ID = StringField(max_length=25, choices=('male', 'female'))
    confidence = FloatField()

    def serialize(self):
        if self.confidence is not None:
            return OrderedDict([
                ('ID', self.ID),
                ('confidence', self.confidence),
            ])
        return self.ID

    def empty(self):
        return self.ID is None