from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

from apps.utils.services import TranskribusSession
from apps.utils.utils import t_log


from .models import TSData
import sys

"""
This backend will

a) override authenticate so that it uses read.services.t_login to authenticate against transkcribus REST
b) on success pass back username
c) match username to existing django user OR create a new dango user
b) set any data that is extra to default django user from
        1) user data retirned by TS REST
        2) user data that is local to the app
"""

class TranskribusBackend(object):

    def authenticate(self, username=None, password=None):
        
        # Make transkribus session here
        # In projects where we need unauthenticated access this is not the place to put it... 
        # or maybe we can use the django anonymous user 
        t = TranskribusSession()
        # Do the login using the TranskribusSession
        t_user = t.login(username, password)
       
        if t_user:
            try:
                user = User.objects.get(username=t_user['userName'])
                #TODO need to update the TSdata if changed (affiliation, gender etc)
            except User.DoesNotExist:
                # Create a new user. password is not chekced so we don't store it here
                user = User(username=t_user['userName'])
            #Transkribus has authority here so update the user data each time...
            user.email = t_user['email']
            user.first_name = t_user['firstname']
            user.last_name = t_user['lastname']
            if t_user['isAdmin'] == 'true':
                user.is_staff = True
            user.save()
            #Extend the user object with some extra data from transkribus
            try:
                tsdata = TSData.objects.get(user=user)
            except TSData.DoesNotExist:
                # we can store the transkribus session as a pickled field, probably better in request.session
                # but we need django 1.11 which passes request to the authenticate backend
                tsdata = TSData.objects.create(user=user,t=t)
            tsdata.gender=t_user['gender']
            tsdata.affiliation=t_user['affiliation']
            tsdata.userId=t_user['userId']

            ######
            # If we have some local user data that we need to update dependent on whatever TS-REST returns do so here
            ######

            tsdata.save()

            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
