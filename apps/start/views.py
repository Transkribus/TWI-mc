from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils import translation
from django.core.mail import send_mail
from django.core import serializers
from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib import messages

from apps.utils.services import TranskribusSession
from django.core.files.storage import default_storage
import uuid 
import os
from . import models as m
from itertools import chain

#from .forms import NameForm
import datetime
import json

#from . import Services as serv 

ts = TranskribusSession()

def index(request):
    template = loader.get_template('start/homepage.html')
    context = {
        'blogs' : m.BlogEntry.objects.filter(lang=translation.get_language()).select_related().order_by('-blog__changed')
    }
    return HttpResponse(template.render(context, request))


def blog_detail(request):
    idb = request.GET.get('id',0)
    print(idb +  ":" + translation.get_language())
    template = loader.get_template('start/blog_detail.html')
    be = m.BlogEntry.objects.get(blog=idb, lang=translation.get_language())
    #b = m.Blog.objects.get(pk=idb)

    context = {
        #'blog' : b,
        'entry' : be
    }
    
    return HttpResponse(template.render(context, request))

def admin(request):   
    template = loader.get_template('start/admin.html')
    b = m.BlogEntry.objects.filter(lang=translation.get_language())
    i = m.Institution.objects.all()
    context = {
        'blogs' : b,
        'inst' : i 
    }

    return HttpResponse(template.render(context, request))


def store_admin_blog(request):
    idb = request.POST.get('id',0)
    if idb == "0":
        title_de = request.POST.get('title_de','')
        title_en = request.POST.get('title_en','')
        subtitle_de = request.POST.get('subtitle_de','')
        subtitle_en = request.POST.get('subtitle_en','')
        content_de = request.POST.get('content_de','')
        content_en = request.POST.get('content_en','')
        print("CONTENT_DE:" + content_de)
        print("CONTENT_EN:" + content_en)
        
        fname = None
        if "blog_name" in request.session:
            fname = request.session["blog_fname"]
            del request.session["blog_fname"]
        b = m.Blog.objects.create(image=fname)
       
        m.BlogEntry.objects.create(title=title_de, subtitle=subtitle_de, content=content_de, blog=b, lang="de")
        m.BlogEntry.objects.create(title=title_en, subtitle=subtitle_en, content=content_en, blog=b, lang="en")  
        
    #b = m.BlogEntry.objects.filter(lang=translation.get_language())  
    #data = serializers.serialize('json', b)    
    #print(json.dumps(json.loads(data), indent=4)) 
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = '{"id" : ' + str(b.pk) + ', "title" : "' + title  + '", "changed" : "' + str(b.changed) + '"}'
    print (json)
    return HttpResponse(json, content_type="application/json")

'''
Find a Blog Entry and return as json
This special task is necessary because joined tables cannot be fully serialized
'''
def get_blog_entry(idb):
    be = m.BlogEntry.objects.filter(blog=idb)
    b = m.Blog.objects.filter(pk=idb)
    combined = list(chain(b, be))
    return serializers.serialize('json', combined)

def change_admin_blog(request):
    idb = request.POST.get('id',0)
    data = get_blog_entry(idb)  

    print(json.dumps(json.loads(data), indent=4)) 
    return HttpResponse(data, content_type="application/json")
    
def delete_admin_blog(request):
    idb = request.POST.get('id',0)
    m.Blog.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")
    

# def store_admin(request):
#     print("store_admin")
#     #TODO limit access to logged in admins
#     title = request.POST.get('title','')
#     content = request.POST.get('content','')
#     id = request.POST.get('id','')
#     lang = request.POST.get('lang','')
# 
#     try:
#       art = m.Article.objects.get(a_key = id, language=lang)
#       art.content = content
#       art.title = title
#       art.save() #add or update
#     except ObjectDoesNotExist:
#       art = m.Article.objects.create(a_key = id, content = content, title=title, language=lang)
#         
#     return HttpResponseRedirect("admin")
#     
    
def logout_process(request):
    ts.invalidate()
    del request.session['user']
    request.session.modified = True
    return HttpResponseRedirect("index")
 
def login_process(request):
    e = request.POST.get('email','')
    p = request.POST.get('password','')
      
    try:
        request.session['user'] = ts.login(e,p)
        request.session.modified = True 
        
    except:
        messages.warning(request, "login_failed")
     
    return HttpResponseRedirect("index")

def register_process(request):
#     user = request.POST.get('user')
#     pw = request.POST.get('pw')
#     pw_again = request.POST.get('pw_again')
#     firstName = request.POST.get('firstName')
#     lastName = request.POST.get('lastName')
#     orcid = request.POST.get('orcid')
#     gender = request.POST.get('gender')
    
    #TODO currently not working
    ts.register(request)
    
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
# Services
# ############################################################

def upload_img(request):
    file = request.FILES['file']
    type = request.POST.get('type')
    #blog_id = request.POST.get('blog_id')
    fname = str(uuid.uuid4()) + "." + os.path.splitext(str(file))[1][1:].strip() 
    path = default_storage.save(settings.IMG_DIR + fname, ContentFile(file.read()))
    request.session[type + "_fname"] = fname
    request.session.modified = True
    
    print("path:" + path)
    print("fname:" + fname)
    
    return HttpResponse(json.dumps(fname), content_type="application/json") 

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


    