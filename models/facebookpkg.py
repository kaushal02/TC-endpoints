from mongoengine import Document, StringField, URLField
from collections import OrderedDict
from helper import empty

class Facebook(Document):
    url = StringField(primary_key=True)
    name = StringField()
    photo = URLField()

    def serialize(self):
        ret = OrderedDict()
        if not empty(self.name):
            ret.update({'name': self.name})
        ret.update({'url': self.url})
        if not empty(self.photo):
            ret.update({'photo': self.photo})
        if len(ret) > 1:
            return ret
        return self.url

    def empty(self):
        return self.url is None