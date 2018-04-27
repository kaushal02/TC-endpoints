from collections import OrderedDict
from datetime import datetime
from mongoengine import (
    Document,
    ListField,
    EmailField,
    StringField,
    DateTimeField,
    ReferenceField,
    EmbeddedDocumentField,
)

from models.facebookpkg import Facebook
from models.genderpkg import Gender
from models.statspkg import Stats
from helper import empty

class Phone(Document):
    ID = StringField(primary_key=True)
    confidence = StringField()
    name = StringField()
    gender = EmbeddedDocumentField(Gender)
    email = EmailField()
    facebook = ReferenceField(Facebook)
    addresses = ListField(StringField())
    metadata = EmbeddedDocumentField(Stats, default=Stats())

    def serialize(self, print_time=False):
        ret = OrderedDict([('ID', self.ID)])
        if not empty(self.confidence):
            ret.update({'confidence': self.confidence})
        if not empty(self.name):
            ret.update({'name': self.name})
        if not self.gender.empty():
            ret.update({'gender': self.gender.serialize()})
        if not empty(self.email):
            ret.update({'email': self.email})
        if self.facebook and not self.facebook.empty():
            ret.update({'facebook': self.facebook.serialize()})
        if len(self.addresses):
            ret.update({'addresses': self.addresses})
        if print_time:
            ret.update({'metadata': self.metadata.serialize()})
        return ret

    def expired(self):
        return self.metadata.expired()

    # @queryset_manager
    # def objects(doc_cls, queryset):
    #     return queryset.order_by('-metadata__created')