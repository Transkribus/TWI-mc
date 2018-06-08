from django.db import models

from django.contrib.auth.models import AbstractUser


from . import helpers


class User(AbstractUser):

    def __str__(self):
        return "{!s}".format(self.username)

    @classmethod
    def create(self, **data):
        # raise Exception(repr(data))
        return self.objects.create(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            # is_active=data['is_active'],
            # is_staff=data['is_staff'],
            is_superuser=data['is_superuser'],

        )

    def update(self, **data):
        helpers.update_changed(self, data, [
            'username', 'email', 'last_name', 'first_name', 'is_superuser', # 'is_staff'
        ])

    def is_developer(self):
        return self.groups.filter(name='Developers').exists()
    
    # NOTE: backwards compatibility
    @property
    def tsdata(self):

        user = self

        from compat.services import TranskribusSession
        cookies = {'JSESSIONID': self.data.session_id}
        trp_sess = TranskribusSession()
        trp_sess.s.cookies.update(cookies)
        
        class _:
            t = trp_sess
            userId = self.data.user_id
            sessionId = self.data.session_id
        return _


class UserData(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='data')
    user_id = models.PositiveIntegerField()
    # NOTE: use this for API requests
    session_id = models.CharField(max_length=32)
    gender = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    # ip = models.IPAddressField(null=True)

    @classmethod
    def create(self, **data):
        return self.objects.create(
            owner=data['owner'],
            user_id=data['user_id'],
            gender=data['gender'],
            affiliation=data['affiliation'],
            session_id=data['session_id'],
        )

    def update(self, **data):
        helpers.update_changed(self, data, [
            'session_id', 'user_id',
            'gender', 'affiliation',
        ])
