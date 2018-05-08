from django.db import models
from django.contrib.auth import get_user_model

class Config(models.Model):
    owner = models.OneToOneField(get_user_model())
    # all the fields ...
