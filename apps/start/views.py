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
        'docs' : m.DocumentEntries.objects.filter(lang=translation.get_language())
        
        
        
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
    i = m.InstitutionDescription.objects.filter(lang=translation.get_language())
    a = m.HomeArticleEntry.objects.filter(lang=translation.get_language())
    q = m.QuoteEntries.objects.filter(lang=translation.get_language())
    v = m.VideoDesc.objects.filter(lang=translation.get_language())
    docs = m.DocumentEntries.objects.filter(lang=translation.get_language())
    ifirst = m.Institution.objects.first()
    
    inst_entries = []
    if ifirst:
        inst_proj_entries = m.InstitutionProjectEntries.objects.filter(project__inst=ifirst.pk, lang=translation.get_language())
    
    context = {
        'blogs' : b,
        'inst' : i,
        'first_inst_proj_entries' : inst_proj_entries,
        'articles' : a,
        'quotes' : q,
        'videos' : v,
        'docs' : docs 
    }

    return HttpResponse(template.render(context, request))

def store_admin_article(request):
    idb = int(request.POST.get('id',0))

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
        

    if idb == 0:
        art = m.HomeArticle.objects.create(image=fname)
        m.HomeArticleEntry.objects.create(title=title_de, shortdesc=subtitle_de, content=content_de, article=art, lang="de")
        m.HomeArticleEntry.objects.create(title=title_en, shortdesc=subtitle_en, content=content_en, article=art, lang="en")  
    else:
        print(idb)
        art = m.HomeArticle.objects.get(pk=idb)
        if fname != None:
            art.update(image=fname)
        m.HomeArticleEntry.objects.filter(article=art, lang="de").update(title=title_de, shortdesc=subtitle_de, content=content_de) 
        m.HomeArticleEntry.objects.filter(article=art, lang="en").update(title=title_en, shortdesc=subtitle_en, content=content_en)
                    
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = '{"id" : ' + str(art.pk) + ', "title" : "' + title  + '", "changed" : "' + str(art.changed) + '"}'
    return HttpResponse(json, content_type="application/json")
              
def store_admin_blog(request):
    idb = int(request.POST.get('id',0))
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
        
    if idb == 0:
        b = m.Blog.objects.create(image=fname)
        m.BlogEntry.objects.create(title=title_de, subtitle=subtitle_de, content=content_de, blog=b, lang="de")
        m.BlogEntry.objects.create(title=title_en, subtitle=subtitle_en, content=content_en, blog=b, lang="en")  
    else:
        b = m.Blog.objects.get(pk=idb) 
        if fname != None:
            b.update(image=fname)
        m.BlogEntry.objects.filter(blog=b, lang="de").update(title=title_de, subtitle=subtitle_de, content=content_de)
        m.BlogEntry.objects.filter(blog=b, lang="en").update(title=title_en, subtitle=subtitle_en, content=content_en)
            
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = '{"id" : ' + str(b.pk) + ', "title" : "' + title  + '", "changed" : "' + str(b.changed) + '"}'
    return HttpResponse(json, content_type="application/json")


def store_admin_inst(request):
    idb = int(request.POST.get('id',0))
    
    name_de = request.POST.get('name_de','')
    loc_name_de = request.POST.get('loc_name_de','')
    name_en = request.POST.get('name_en','')
    loc_name_en = request.POST.get('loc_name_en','')
    lng = Decimal(request.POST.get('lng',''))
    lat = Decimal(request.POST.get('lat',''))
    url = request.POST.get('url','')
    content_de = request.POST.get('content_de','')    
    content_en = request.POST.get('content_en','')

    fname = None
    if "inst_fname" in request.session:
        fname = request.session["inst_fname"]
        del request.session["inst_fname"]
    
    if idb == 0:        
        inst = m.Institution.objects.create(lng=lng, lat=lat, link=url, image=fname)
        m.InstitutionDescription.objects.create(name=name_de, loclabel=loc_name_de, desc=content_de, lang='de', inst=inst)
        m.InstitutionDescription.objects.create(name=name_en, loclabel=loc_name_en, desc=content_en, lang='en', inst=inst)   
    else:
        inst = m.Institution.objects.get(pk=idb)
        if fname != None:
            inst.update(image=fname, lng=lng, lat=lat, link=url)
        m.InstitutionDescription.objects.filter(lang='de', inst=inst).update(name=name_de, loclabel=loc_name_de, desc=content_de)
        m.InstitutionDescription.objects.filter(lang='en', inst=inst).update(name=name_en, loclabel=loc_name_en, desc=content_en)
                    
    name = (name_de, name_en)[translation.get_language() == 'de']
    json = '{"id" : ' + str(inst.pk) + ', "name" : "' + name + '", "changed" : "' + str(inst.changed) + '"}'
    return HttpResponse(json, content_type="application/json") 

def store_admin_inst_proj(request):
    idb = int(request.POST.get('id',0))

    inst_id = request.POST.get('inst_id',0)
    title_de = request.POST.get('title_de','')
    title_en = request.POST.get('title_en','')
    content_de = request.POST.get('content_de','')
    content_en = request.POST.get('content_en','')
    print(idb)
    if idb == 0:
        p = m.InstitutionProject.objects.create(inst=m.Institution.objects.get(pk=inst_id))
        m.InstitutionProjectEntries.objects.create(title=title_de, desc=content_de, lang='de', project=p)
        m.InstitutionProjectEntries.objects.create(title=title_en, desc=content_en, lang='en', project=p)        
    else:
        p = m.InstitutionProject.objects.get(pk=idb)
        m.InstitutionProjectEntries.objects.filter(lang='de', project=p).update(title=title_de, desc=content_de)
        m.InstitutionProjectEntries.objects.filter(lang='en', project=p).update(title=title_en, desc=content_en)
                
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = '{"id" : ' + str(p.pk) + ', "title" : "' + title  + '", "changed" : "' + str(p.changed) + '"}'
    return HttpResponse(json, content_type="application/json") 


def store_admin_quote(request):
    idb = int(request.POST.get('id',0))
 
    role_de = request.POST.get('role_de','')
    role_en = request.POST.get('role_en','')
    content_de = request.POST.get('content_de','')
    content_en = request.POST.get('content_en','')
    name = request.POST.get('name','')
    
    fname = None
    if "quote_fname" in request.session:
        fname = request.session["quote_fname"]
        del request.session["quote_fname"]
    
    
    print("ID" + str(idb))
    if idb == 0:
        q = m.Quote.objects.create(name=name, image=fname)
        m.QuoteEntries.objects.create(content=content_de, role=role_de, lang='de', quote=q)
        m.QuoteEntries.objects.create(content=content_en, role=role_en, lang='en', quote=q)
    else:
        q = m.Quote.objects.filter(pk=idb)
        q.update(name=name);
        m.QuoteEntries.objects.filter(lang='de', quote=q).update(content=content_de, role=role_de)
        m.QuoteEntries.objects.filter(lang='en', quote=q).update(content=content_en, role=role_en)
        
    json = '{"id" : ' + str(q.first().id) + ', "name" : "' + name + '"}'
    print (json);
    return HttpResponse(json, content_type="application/json") 

def store_admin_doc(request):
    idb = int(request.POST.get('id',0))
    title_de = request.POST.get('title_de','')
    title_en =request.POST.get('title_en','')
    desc_en =request.POST.get('desc_en','')
    desc_de = request.POST.get('desc_de','')
    content_en = request.POST.get('content_en','')
    content_de = request.POST.get('content_de','')
    icon = request.POST.get('icon','')
    
    if idb == 0:
        d = m.Document.objects.create(icon=icon)
        m.DocumentEntries.objects.create(title=title_de, desc=desc_de, content=content_de, doc=d, lang='de')
        m.DocumentEntries.objects.create(title=title_en, desc=desc_en, content= content_en, doc=d, lang='en')
    else:
        d = d = m.Document.objects.filter(pk=idb)
        d.update(icon=icon)
        m.DocumentEntries.objects.filter(doc=d, lang='de').update(title=title_de, desc=desc_de, content=content_de)
        m.DocumentEntries.objects.filter(doc=d, lang='en').update(title=title_en, desc=desc_en, content= content_en)
        
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = '{"id" : ' + str(d.pk) + ', "title" : "' + title +  '", "changed" : "' + str(d.changed) + '"}'
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


def change_admin_quote_selection(request):
    idb = request.POST.get('id',0)
    qe = m.QuoteEntries.objects.filter(quote=idb)
    q = m.Quote.objects.filter(pk=idb)
    data = list(chain(q, qe))
    data = serializers.serialize('json',data)
    print(json.dumps(json.loads(data), indent=4)) 
    return HttpResponse(data, content_type="application/json")   

'''
is called when the project entries should be changed in the institution/project area
'''
def change_admin_inst_proj_selection(request):
    idb = request.POST.get('id',0)
    ipe = m.InstitutionProjectEntries.objects.filter(project=idb)
    print(idb)
    js = serializers.serialize('json',ipe)
    print(js) 
    return HttpResponse(js, content_type="application/json")  


def change_admin_doc_selection(request):
    idb = request.POST.get('id',0)
    
    de = m.DocumentEntries.objects.filter(doc=idb)
    d = m.Document.objects.filter(pk=idb)
    data = list(chain(d, de))
    data = serializers.serialize('json', data)
    print(json.dumps(json.loads(data), indent=4)) 
    return HttpResponse(data, content_type="application/json")

def change_admin_video_selection(request):
    idb = request.POST.get('id',0)
    v = m.Video.objects.filter(pk=idb)
    ve = m.VideoDesc.objects.filter(video__pk=idb)
    data = list(chain(v, ve))
    data = serializers.serialize('json', data)
    print(json.dumps(json.loads(data), indent=4)) 
    return HttpResponse(data, content_type="application/json")

def change_admin_article(request):
    idb = request.POST.get('id',0)
    be = m.HomeArticleEntry.objects.filter(article=idb)
    b = m.HomeArticle.objects.filter(pk=idb)
    data = list(chain(b, be))
    data = serializers.serialize('json', data)
    return HttpResponse(data, content_type="application/json")


def delete_admin_article(request):
    idb = request.POST.get('id',0)
    m.HomeArticle.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

def delete_admin_projinst(request):
    idb = request.POST.get('id',0)
    m.InstitutionProject.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")
  
  
def delete_admin_quote(request):
    idb = request.POST.get('id',0)
    m.Quote.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

def delete_admin_doc(request):
    idb = request.POST.get('id',0)
    m.Document.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

def delete_admin_video(request):
    idb = request.POST.get('id',0)
    m.Video.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

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
    print(idb)
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
    


    