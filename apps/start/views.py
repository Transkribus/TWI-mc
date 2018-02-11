from django.shortcuts import render
from fluent_contents.models import Placeholder

from . import models as m

from .forms import NameForm

# Create your views here.

def index(request):
    return render(request, 'start/homepage.html' )

def admin(request):

        
    template = loader.get_template()
    return HttpResponse(template.render(context, request))





def admin(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'start/admin.html', {'form': form})