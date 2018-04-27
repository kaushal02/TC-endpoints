from collections import OrderedDict
from mongoengine import (
    Document,
    IntField,
    URLField,
    ListField,
    StringField,
    BooleanField,
    DateTimeField,
    EmbeddedDocumentField,
)

from models.genderpkg import Gender
from models.statspkg import Stats
from helper import empty

class Email(Document):
    ID = StringField(primary_key=True)
    # all the fields below are missing for non-Google accounts
    name = StringField()
    gender = EmbeddedDocumentField(Gender)
    birthday = StringField()
    verified = BooleanField()
    friends = IntField()
    photo = URLField()
    profile = URLField()
    addresses = ListField(StringField())
    external_profiles = ListField(URLField())
    metadata = EmbeddedDocumentField(Stats, default=Stats())

    def serialize(self, print_time=False):
        ret = OrderedDict([('ID', self.ID)])
        if not empty(self.name):
            ret.update({'name': self.name})
        if self.gender and not self.gender.empty():
            ret.update({'gender': self.gender.serialize()})
        if not empty(self.birthday):
            ret.update({'birthday': self.birthday})
        if not empty(self.verified):
            ret.update({'verified': self.verified})
        if not empty(self.friends):
            ret.update({'friends': self.friends})
        if not empty(self.photo):
            ret.update({'photo': self.photo})
        if not empty(self.profile):
            ret.update({'profile': self.profile})
        if len(self.addresses):
            ret.update({'addresses': self.addresses})
        if len(self.external_profiles):
            ret.update({'external_profiles': self.external_profiles})
        if print_time:
            ret.update({'metadata': self.metadata.serialize()})
        return ret

    def expired(self):
        return self.metadata.expired()

    