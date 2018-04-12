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
from decimal import Decimal
from apps.utils.services import TranskribusSession
from django.core.files.storage import default_storage
import uuid 
import os
from random import randint
from . import models as m
from itertools import chain

#from .forms import NameForm
import datetime
import json

#from . import Services as serv 

ts = TranskribusSession()

def index(request):
    template = loader.get_template('start/homepage.html')
    subscribed_users = randint(0,1000)
    collaborations = randint(0,1000)
    uploaded_docs = randint(0,1000)
    trained_models = randint(0,1000)
    
    context = {
        'blogs' : m.BlogEntry.objects.filter(lang=translation.get_language()).select_related().order_by('-blog__changed'),
        'inst' :  m.Institution.objects.all(),
        'articles' : m.HomeArticleEntry.objects.filter(lang=translation.get_language()),
        'service' : m.ServiceEntries.objects.filter(lang=translation.get_language()),
        'quotes' : m.QuoteEntries.objects.filter(lang=translation.get_language()),
        'videos' : m.VideoDesc.objects.filter(lang=translation.get_language()),
        'subscribed_users' : subscribed_users,
        'collaborations': collaborations,
        'uploaded_docs' : uploaded_docs,
        'trained_models' : trained_models,
        'docs' : m.DocumentEnrtries.filter(lang=translation.get_language())
        
        
        
    }
    return HttpResponse(template.render(context, request))

def inst_detail(request):
    idb = request.GET.get('id',0)
    template = loader.get_template('start/inst_detail.html')
    inst = m.Institution.objects.get(pk=idb)
    desc = m.InstitutionDescription.objects.get(inst=inst, lang=translation.get_language())
    proj = m.InstitutionProjectEntries.objects.filter(project__inst=inst, lang=translation.get_language())
    
    
    context = {
        'inst' : inst,
        'desc' : desc,
        'proj' : proj
    }
    
    return HttpResponse(template.render(context, request))

def home_article_details(request):
    idb = request.GET.get('id',0)
    context = {
        'article' : m.HomeArticleEntry.objects.get(article=idb, lang=translation.get_language())
    }
    
    template = loader.get_template('start/home_article_detail.html')
    
    return HttpResponse(template.render(context, request))
    
def blog_detail(request):
    idb = request.GET.get('id',0)
    print(idb +  ":" + translation.get_language())
    template = loader.get_template('start/blog_detail.html')
    be = m.BlogEntry.objects.get(blog=idb, lang=translation.get_language())
    #b = m.Blog.objects.get(pk=idb)

    context = {
        #'blog' : b,
        'blog' : be,
    }
 
    return HttpResponse(template.render(context, request))

def admin(request):   
    template = loader.get_template('start/admin.html')
    b = m.BlogEntry.objects.filter(lang=translation.get_language())
    i = m.Institution.objects.all()
    a = m.HomeArticleEntry.objects.filter(lang=translation.get_language())
    q = m.QuoteEntries.objects.filter(lang=translation.get_language())
    v = m.VideoDesc.objects.filter(lang=translation.get_language())
    docs = m.DocumentEnrtries.filter(lang=translation.get_language())
    ifirst = m.Institution.objects.first()
    inst_entries = []
    if ifirst:
        inst_entries = m.InstitutionProjectEntries.objects.filter(project__inst=ifirst.pk, lang=translation.get_language())
    
    
    context = {
        'blogs' : b,
        'inst' : i,
        'first_inst_entries' : inst_entries,
        'articles' : a,
        'quotes' : q,
        'videos' : v,
        'docs' : docs 
    }

    return HttpResponse(template.render(context, request))

def store_admin_article(request):
    idb = request.POST.get('id',0)
    if idb == "0":
        title_de = request.POST.get('title_de','')
        title_en = request.POST.get('title_en','')
        subtitle_de = request.POST.get('subtitle_de','')
        subtitle_en = request.POST.get('subtitle_en','')
        content_de = request.POST.get('content_de','')
        content_en = request.POST.get('content_en','')
            
        fname = None
        if "article_fname" in request.session:
            fname = request.session["article_fname"]
            del request.session["article_fname"]
        art = m.HomeArticle.objects.create(image=fname)
       
        m.HomeArticleEntry.objects.create(title=title_de, shortdesc=subtitle_de, content=content_de, article=art, lang="de")
        m.HomeArticleEntry.objects.create(title=title_en, shortdesc=subtitle_en, content=content_en, article=art, lang="en")  
        
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = '{"id" : ' + str(art.pk) + ', "title" : "' + title  + '", "changed" : "' + str(art.changed) + '"}'
    print (json)
    return HttpResponse(json, content_type="application/json")
      
        
def store_admin_blog(request):
    idb = request.POST.get('id',0)
    if idb == "0":
        title_de = request.POST.get('title_de','')
        title_en = request.POST.get('title_en','')
        subtitle_de = request.POST.get('subtitle_de','')
        subtitle_en = request.POST.get('subtitle_en','')
        content_de = request.POST.get('content_de','')
        content_en = request.POST.get('content_en','')
            
        fname = None
        if "blog_fname" in request.session:
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


def store_admin_inst(request):
    print("store_admin_inst")
    idb = request.POST.get('id',0)
    if idb == "0":
        name = request.POST.get('name','')
        loc_name = request.POST.get('loc_name','')
        lng = Decimal(request.POST.get('lng',''))
        lat = Decimal(request.POST.get('lat',''))
        url = request.POST.get('url','')
        
        fname = None
        if "inst_fname" in request.session:
            fname = request.session["inst_fname"]
            del request.session["inst_fname"]
        
        inst = m.Institution.objects.create(name=name, loclabel=loc_name, lng=lng, lat=lat, link=url, image=fname)
        
        content_de = request.POST.get('content_de','')
        m.InstitutionDescription.objects.create(desc=content_de, lang='de', inst=inst)
        
        content_en = request.POST.get('content_en','')
        m.InstitutionDescription.objects.create(desc=content_en, lang='en', inst=inst)   
    json = '{"name" : ' + name + '}'
    print (json)
    return HttpResponse(json, content_type="application/json") 

def store_admin_inst_proj(request):
    idb = request.POST.get('id',0)
    if idb == "0":
        inst_id = request.POST.get('inst_id',0)
        title_de = request.POST.get('title_de','')
        title_en = request.POST.get('title_en','')
        content_de = request.POST.get('content_de','')
        content_en = request.POST.get('content_en','')
        print("inst_id:" + str(inst_id))
        p = m.InstitutionProject.objects.create(inst=m.Institution.objects.get(pk=inst_id))
        m.InstitutionProjectEntries.objects.create(title=title_de, desc=content_de, lang='de', project=p)
        m.InstitutionProjectEntries.objects.create(title=title_en, desc=content_en, lang='en', project=p)        
 
        title = (title_de, title_en)[translation.get_language() == 'de']
        json = '{"id" : ' + str(p.pk) + ', "title" : "' + title + '"}'
        return HttpResponse(json, content_type="application/json") 


def store_admin_quote(request):
    idb = request.POST.get('id',0)
    print("ID" + str(idb))
    #if idb == 0:
    
    role_de = request.POST.get('role_de','')
    role_en = request.POST.get('role_en','')
    content_de = request.POST.get('content_de','')
    content_en = request.POST.get('content_en','')
    name = request.POST.get('name','')
    
    fname = None
    if "quote_fname" in request.session:
        fname = request.session["quote_fname"]
        del request.session["quote_fname"]
    
    q = m.Quote.objects.create(name=name, image=fname);
    m.QuoteEntries.objects.create(content=content_de, role=role_de, lang='de', quote=q)
    m.QuoteEntries.objects.create(content=content_en, role=role_en, lang='en', quote=q)
    
#     title = (role_de, role_en)[translation.get_language() == 'de']
    json = '{"id" : ' + str(q.pk) + ', "title" : "' + name + '"}'
    return HttpResponse(json, content_type="application/json") 


def store_admin_video(request):
    idb = request.POST.get('id',0)
    vid = request.POST.get('vid','')
    title_de = request.POST.get('title_de','')
    title_en = request.POST.get('title_en','')
    content_de = request.POST.get('content_de','')
    content_en = request.POST.get('content_en','')
    
    v = m.Video.objects.create(vid = vid)
    m.VideoDesc.objects.create(title=title_de, desc=content_de, lang='de', video=v)
    m.VideoDesc.objects.create(title=title_en, desc=content_en, lang='en', video=v)    

    title = (title_de, title_en)[translation.get_language() == 'de']
    json = '{"id" : ' + str(v.pk) + ', "title" : "' + title + ' (' + vid + ')"}'
    return HttpResponse(json, content_type="application/json")     

'''
is called when another institution is selected in the institution/project area
'''
def change_admin_inst_proj(request):
    idb = request.POST.get('id',0)
    ipe = m.InstitutionProjectEntries.objects.filter(project__pk=idb, lang=translation.get_language())

    js = serializers.serialize('json',ipe)
    print(js) 
    return HttpResponse(js, content_type="application/json")    


def change_admin_inst_proj_selection(request):
    idb = request.POST.get('id',0)
    ipe = m.InstitutionProjectEntries.objects.filter(project=idb)

    js = serializers.serialize('json',ipe)
    print(js) 
    return HttpResponse(js, content_type="application/json")  




def change_admin_article(request):
    idb = request.POST.get('id',0)
    be = m.HomeArticleEntry.objects.filter(article=idb)
    b = m.HomeArticle.objects.filter(pk=idb)
    data = list(chain(b, be))
    data = serializers.serialize('json', data)
    return HttpResponse(data, content_type="application/json")

'''
Find a Blog Entry and return as json
This special task is necessary because joined tables cannot be fully serialized as json
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

def delete_admin_inst(request):
    idb = request.POST.get('id',0)
    m.Institution.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

'''
Find a Institution Entry and return as json
This special task is necessary because joined tables cannot be fully serialized as json
'''
def get_inst_entry(idb):
    be = m.InstitutionDescription.objects.filter(inst=idb)
    b = m.Institution.objects.filter(pk=idb)
    combined = list(chain(b, be))
    return serializers.serialize('json', combined)

 
def change_admin_inst(request):   
    idb = request.POST.get('id',0)
    data = get_inst_entry(idb)  

    print(json.dumps(json.loads(data), indent=4)) 
    return HttpResponse(data, content_type="application/json")

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
#     for i in range(1,9):        
#         m.Article.objects.create(a_key=i, language="DE", title="TD" + str(i), content="<b>content TD" + str(i) + "</b>", changed=datetime.date)
#         m.Article.objects.create(a_key=i, language="EN", title="TE" + str(i), content="<b>content TE" + str(i) + "</b>", changed=datetime.date)
    s = m.Service.objects.create(image_css='icon-strategy')
    m.ServiceEntries.objects.create(title='Discover the power of keyword spotting', subtitle='Keyword spotting is a magic way to search directly in the image. You will be able to explore every word you are looking for in a collection of highly diverse documents', content='C_de', lang='de', service=s)
    m.ServiceEntries.objects.create(title='Discover the power of keyword spotting', subtitle='Keyword spotting is a magic way to search directly in the image. You will be able to explore every word you are looking for in a collection of highly diverse documents', content='C_en', lang='en', service=s)

    s = m.Service.objects.create(image_css='icon-lightbulb')
    m.ServiceEntries.objects.create(title='Organize your project', subtitle='Upload as many documents you want, train your specific text recognition models, invite collegues, share your documents and models with colleges, export documents in any format at any time…', content='C_de', lang='de', service=s)
    m.ServiceEntries.objects.create(title='Organize your project', subtitle='Upload as many documents you want, train your specific text recognition models, invite collegues, share your documents and models with colleges, export documents in any format at any time…', content='C_en', lang='en', service=s)

    s = m.Service.objects.create(image_css='icon-lightbulb')
    m.ServiceEntries.objects.create(title='Manage your private collection', subtitle='All documents are private in your personal Transkribus collection. Therefore enjoy the benefits of copyright exceptions available for personal use and research. ', content='C_de', lang='de', service=s)
    m.ServiceEntries.objects.create(title='Manage your private collection', subtitle='All documents are private in your personal Transkribus collection. Therefore enjoy the benefits of copyright exceptions available for personal use and research. ', content='C_en', lang='en', service=s)

    s = m.Service.objects.create(image_css='icon-lightbulb')
    m.ServiceEntries.objects.create(title='Create your own neural network', subtitle='Transcribe some dozens of pages, train a neural network and recognize hundreds or thousands of documents, or transcribe faster than before…', content='C_de', lang='de', service=s)
    m.ServiceEntries.objects.create(title='Create your own neural network', subtitle='Transcribe some dozens of pages, train a neural network and recognize hundreds or thousands of documents, or transcribe faster than before…', content='C_en', lang='en', service=s)
 
    s = m.Service.objects.create(image_css='icon-lightbulb')
    m.ServiceEntries.objects.create(title='Transcribe in a highly standardized way', subtitle='Be it ancient Greek, Arabic or Latin, or a modern language you will be able to create a transcription on the highest scholarly level including annotations and comments.', content='C_de', lang='de', service=s)
    m.ServiceEntries.objects.create(title='Transcribe in a highly standardized way', subtitle='Be it ancient Greek, Arabic or Latin, or a modern language you will be able to create a transcription on the highest scholarly level including annotations and comments.', content='C_en', lang='en', service=s)
 
    
    s = m.Service.objects.create(image_css='icon-lightbulb')
    m.ServiceEntries.objects.create(title='Collaborate with colleagues and share your documents', subtitle='Organize your project as a collaborative effort. Work at different places but in one collection. Export your documents or share them via the web-interface', content='C_de', lang='de', service=s)
    m.ServiceEntries.objects.create(title='Collaborate with colleagues and share your documents', subtitle='Organize your project as a collaborative effort. Work at different places but in one collection. Export your documents or share them via the web-interface', content='C_en', lang='en', service=s)        
    
    s = m.Service.objects.create(image_css='icon-lightbulb')
    m.ServiceEntries.objects.create(title='Scan your own documents with the smartphone', subtitle='A smartphone as document scanner? Yes, with the ScanTent and DocScan you will be able to scan books and other documents fast, reliable and in an excellent quality.', content='C_de', lang='de', service=s)
    m.ServiceEntries.objects.create(title='Scan your own documents with the smartphone', subtitle='A smartphone as document scanner? Yes, with the ScanTent and DocScan you will be able to scan books and other documents fast, reliable and in an excellent quality.', content='C_en', lang='en', service=s)        
    
    s = m.Service.objects.create(image_css='icon-lightbulb')
    m.ServiceEntries.objects.create(title='Teach students and volunteers to read ancient scripts', subtitle='Students should, volunteers want to be able to read historical scripts. In both cases the only way to get better is: exercise, exercise, exercise on real world material. And by using the mobile phone…', content='C_de', lang='de', service=s)
    m.ServiceEntries.objects.create(title='Teach students and volunteers to read ancient scripts', subtitle='Students should, volunteers want to be able to read historical scripts. In both cases the only way to get better is: exercise, exercise, exercise on real world material. And by using the mobile phone…', content='C_en', lang='en', service=s)        
    
#     s = m.Service.objects.create(image_css='icon-lightbulb')
#     m.ServiceEntries.objects.create(title='', subtitle='', content='C_de', lang='de', service=s)
#     m.ServiceEntries.objects.create(title='', subtitle='', content='C_en', lang='en', service=s)        

    
    return HttpResponse('done', content_type="text/plain")
    


    