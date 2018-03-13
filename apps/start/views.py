from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils import translation
from django.core.mail import send_mail

from apps.utils.services import TranskribusSession
 
from . import models as m
#from .forms import NameForm
import datetime
import json

#from . import Services as serv 

ts = TranskribusSession()

def index(request):
    template = loader.get_template('start/homepage.html')
    context = {
        'articles' : m.Article.objects.filter(language=translation.get_language().upper())
    }
    return HttpResponse(template.render(context, request))

def admin(request):   
    template = loader.get_template('start/admin.html')
    print(translation.get_language())
    td = testData()
    art = m.Article.objects.filter(language=translation.get_language().upper())
    context = {
        'articles' : art 
    }

    return HttpResponse(template.render(context, request))


def store_admin_blog(request):
    print("store_admin_blog")
    id = request.POST.get('id',0)
    print("id:" + id)
    if id == "0":
        title_de = request.POST.get('title_de','')
        title_en = request.POST.get('title_en','')
        subtitle_de = request.POST.get('subtitle_de','')
        subtitle_en = request.POST.get('subtitle_en','')
        content_de = request.POST.get('content_de','')
        content_en = request.POST.get('content_en','')
        print()
        #TODO image storage if available
        b = m.Blog.objects.create()
        
        e_de =m.BlogEntry.objects.create(title=title_de, subtitle=subtitle_de, content=content_de, blog=b, lang="de")
        e_en = m.BlogEntry.objects.create(title=title_de, subtitle=subtitle_de, content=content_de, blog=b, lang="en")  
        print(e_de)
        print(e_en)      
    #return HttpResponseRedirect("start_admin")
    return HttpResponse('ok', content_type="text/plain")

def store_admin(request):
    print("store_admin")
    #TODO limit access to logged in admins
    title = request.POST.get('title','')
    content = request.POST.get('content','')
    id = request.POST.get('id','')
    lang = request.POST.get('lang','')

    try:
      art = m.Article.objects.get(a_key = id, language=lang)
      art.content = content
      art.title = title
      art.save() #add or update
    except ObjectDoesNotExist:
      art = m.Article.objects.create(a_key = id, content = content, title=title, language=lang)
        
    return HttpResponseRedirect("admin")
    
    
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


    