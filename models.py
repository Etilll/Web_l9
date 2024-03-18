
from mongoengine import Document
from mongoengine.fields import ListField, StringField, ReferenceField

class Author(Document):
    fullname = StringField()
    born_date = StringField()
    born_location = StringField()
    description = StringField()
    meta = {'allow_inheritance': True}

class Quote(Document):
    tags = ListField()
    author = ReferenceField(Author)
    quote = StringField()
    meta = {'allow_inheritance': True}
