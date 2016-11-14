#imports of python modules
#import json
#import sys
#import re
#import random

#Imports of django modules
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
#from django.utils import translation
#from django.contrib.auth.models import User
#from django.contrib.auth.decorators import login_required
#from django.contrib import messages
#from django.utils.translation import ugettext_lazy as _
#from django.template.loader import render_to_string

#from read.utils import crop, t_metadata
##Imports pf read modules
#from read.decorators import t_login_required
#from read.services import *
##t_collection, t_register,

##Imports from app (library)
#import library.settings
#from . import navigation
from .forms import RegisterForm

#from profiler import profile #profile is a decorator, but things get circular if I include it in decorators.py so...


def register(request):
#TODO this is generic guff need to extend form for extra fields, send reg data to transkribus and authticate (which will handle the user creation)

    if request.user.is_authenticated(): #shouldn't really happen but...
#        return HttpResponseRedirect(request.build_absolute_uri('/library/'))
        return HttpResponseRedirect(request.build_absolute_uri(request.resolver_match.app_name))
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        sys.stdout.write("### IN t_register \r\n" )
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            sys.stdout.write("### IN form is valid \r\n" )

            # user = User.objects.create_user(form.cleaned_data['username'],password=form.cleaned_data['password'],email=form.cleaned_data['email'],first_name=form.cleaned_data['given_name'],last_name=form.cleaned_data['family_name'])
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            try:
                t_register(request)
                return HttpResponseRedirect(request.build_absolute_uri(request.resolver_match.app_name))
                #tried out modal here and it is nice (but not really for registration)
#               messages.info(request, _('Registration requested please check your email.'))
#                return HttpResponse(json.dumps({'RESET': 'true', 'MESSAGE': render_to_string('library/message_modal.html', request=request)}), content_type='text/plain')
            except ValueError as err:
                sys.stdout.write("### t_register response ERROR RAISED: %s  \r\n" % (err) )
#               return render(request, 'registration/register.html', {'register_form': form} )
                #Why the f**k won't this redirect?!? TODO fix or try another method
                return HttpResponseRedirect(request.build_absolute_uri('/library/error'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegisterForm()

    #Recpatch errors are not properly dislpayed by bootstrap-form... hmph
    return render(request, 'registration/register.html', {'register_form': form} )

