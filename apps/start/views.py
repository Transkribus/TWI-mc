from django.shortcuts import render
from fluent_contents.models import Placeholder
from django.views.generic.detail import DetailView
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils import translation
from django.core.mail import send_mail

from . import models as m
#from .forms import NameForm
import datetime
import json

from . import Services as serv 


def index(request):
    template = loader.get_template('start/homepage.html')
    context = {
        'articles' : m.Article.objects.filter(language="DE")
    }
    return HttpResponse(template.render(context, request))

def admin(request):   
    template = loader.get_template('start/admin.html')
    
    td = testData()
    print(td)
    context = {
        'articles' : td 
    }
    url = static('start/css/admin.css')
    print(url)
    return HttpResponse(template.render(context, request))


def store_admin(request):
    #TODO limit access to logged in admins
    title = request.POST.get('title','')
    content = request.POST.get('content','')
    id = request.POST.get('id','')
    lang = request.POST.get('lang','')

    print(content)
    try:
      art = m.Article.objects.get(a_key = id, language=lang)
      art.content = content
      art.title = title
      art.save() #add or update
    except ObjectDoesNotExist:
      art = m.Article.objects.create(a_key = id, content = content, title=title, language=lang)
        
    return HttpResponse('huhu', content_type="text/plain")
    
    
def logout_process(request):
    s = serv.Services();
    s.Logout()
    del request.session['user']
    request.session.modified = True
    return HttpResponseRedirect("index")
 
def login_process(request):
    e = request.POST.get('email','')
    p = request.POST.get('password','')
  
    s = serv.Services();
    
    try:
        request.session['user'] = s.Login(e,p)['trpUserLogin']
        request.session.modified = True 
        
    except:
        messages.warning(request, "login_failed")
     
    return HttpResponseRedirect("index")

    
def change_lang(request):
    lang = request.GET.get('lang','en')
    translation.activate(lang)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) #redirect to same page

def contact(request):
    full_name = request.POST.get('full_name','')
    email = request.POST.get('email','')
    print (email)
    phone = request.POST.get('phone','')
    message = request.POST.get('message','')
    message += "email:" + email
    send_mail('website message', message, 'albert.greinoecker@gmail.com', ['albert.greinoecker@gmail.com'], fail_silently=False,
)
    
            
# ############################################################
# ############################################################
# ############################################################
    
    
    
def testData():
    articles = []
    for i in range(1,9):        
        articles.append(m.Article(a_key=i, language="DE", title="TD" + str(i), content="<b>content TD" + str(i) + "</b>", changed=datetime.date))
        #articles.append(m.Article(a_key=i, language="EN", title="TE" + str(i), content="<b>content TE1" + str(i) + "</b>", changed=datetime.date))
    return articles
    
# def arrange(articles):
#     rearrg = {}
#     for a in articles:
#         k = a.a_key
#         l = []
#         if k in rearrg:
#             l = rearrg[k]
#         l.append(a)
#         rearrg[k] = l
#     return rearrg


# Handle with care!
def script(request):
    for i in range(1,9):        
        m.Article.objects.create(a_key=i, language="DE", title="TD" + str(i), content="<b>content TD" + str(i) + "</b>", changed=datetime.date)
        m.Article.objects.create(a_key=i, language="EN", title="TE" + str(i), content="<b>content TE" + str(i) + "</b>", changed=datetime.date)
    return HttpResponse('done', content_type="text/plain")


    