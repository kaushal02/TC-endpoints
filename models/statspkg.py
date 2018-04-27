from mongoengine import EmbeddedDocument, DateTimeField
from datetime import datetime, timedelta
from collections import OrderedDict

class Stats(EmbeddedDocument):
    created = DateTimeField(default=datetime.utcnow)
    
    def serialize(self):
        ret = OrderedDict([('created', self.created)])
        return ret

    def expired(self):
        return self.created + timedelta(minutes=1) < datetime.utcnow()