

from django.db import models

# Create your models here.
#class Client(models.Model):
#   email = models.EmailField(unique=True, max_length=100)
#   password = models.CharField(max_length=128)

from django.contrib.auth.models import User
from picklefield.fields import PickledObjectField

from django.conf import settings
class TSData(models.Model):
    pass
    # user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # userId = models.CharField(max_length=100, default=0)
    # gender = models.CharField(max_length=100)
    # affiliation = models.CharField(max_length=100)
    # t = PickledObjectField(null=True)
    # sessionId = models.CharField(max_length=100,null=True,blank=True)
    #Add fields for any user data local to app here
    #thingthatappneedstostoreperuser = models.WhateverField();
