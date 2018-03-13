from django.db import models

from . import transkribus

# https://github.com/Transkribus/TWI-library/issues/37

class Collection(transkribus.Collection):

    class Meta:
        proxy = True

    def __str__(self):
        return "This is a collection."

    def some_method(self):
        raise NotImplementedError


class Document(transkribus.DocMd):

    class Meta:
        proxy = True


class Page(transkribus.Page):

    class Meta:
        proxy = True


class Transcript(transkribus.Transcript):

    class Meta:
        proxy = True
