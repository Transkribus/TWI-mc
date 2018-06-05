import uuid 
import os
from random import randint
from itertools import chain
import datetime
import json
import requests
from PIL import Image
import logging
from locale import format_string
from decimal import Decimal
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils import translation
from django.core.mail import send_mail
from django.core import serializers
from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from apps.utils.services import TranskribusSession
from . import models
from . import decorators


#from . import Services as serv 

ts = TranskribusSession()

# Get an instance of a logger
logger = logging.getLogger(__name__)

def blog_all(request):
    template = loader.get_template('start/blog_all.html')
    context = {
        'blogs' : models.BlogEntry.objects.filter(lang=translation.get_language()).select_related().order_by('-blog__changed'),
    }
    return HttpResponse(template.render(context, request))
    
def login_view(request):
    template = loader.get_template('start/login.html')
    context = { }
    return HttpResponse(template.render(context, request))
 
def index(request):
    template = loader.get_template('start/homepage.html')
    subscribed_users = randint(0,1000)
    collaborations = randint(0,1000)
    uploaded_docs = randint(0,1000)
    trained_models = randint(0,1000)
    
    context = {
        'blogs' : models.BlogEntry.objects.filter(lang=translation.get_language()).select_related().order_by('-blog__changed')[:15],
        'inst' :  models.InstitutionDescription.objects.filter(lang=translation.get_language()),
        'articles' : models.HomeArticleEntry.objects.filter(lang=translation.get_language()),
        'services' : models.ServiceEntries.objects.filter(lang=translation.get_language()),
        'quotes' : models.QuoteEntries.objects.filter(lang=translation.get_language()),
        'videos' : models.VideoDesc.objects.filter(lang=translation.get_language()),
        'subscribed_users' : subscribed_users,
        'collaborations': collaborations,
        'uploaded_docs' : uploaded_docs,
        'trained_models' : trained_models,
        'docs' : models.DocumentEntries.objects.filter(lang=translation.get_language()),
        'recaptcha_key' : settings.RECAPTCHA_KEY 
    }
    return HttpResponse(template.render(context, request))

def inst_detail(request):
    idb = request.GET.get('id',0)
    template = loader.get_template('start/inst_detail.html')
    inst = models.Institution.objects.get(pk=idb)
    desc = models.InstitutionDescription.objects.get(inst=inst, lang=translation.get_language())
    proj = models.InstitutionProjectEntries.objects.filter(project__inst=inst, lang=translation.get_language())
    
    
    context = {
        'inst' : inst,
        'desc' : desc,
        'proj' : proj
    }
    
    return HttpResponse(template.render(context, request))

def home_article_detail(request):
    idb = request.GET.get('id',0)
    context = {
        'article' : models.HomeArticleEntry.objects.get(article=idb, lang=translation.get_language())
    }
    
    template = loader.get_template('start/home_article_detail.html')
    
    return HttpResponse(template.render(context, request))
        
@user_passes_test(decorators.admin_logged_in)
def admin(request):   
    template = loader.get_template('start/admin.html')
    b = models.BlogEntry.objects.filter(lang=translation.get_language())
    i = models.InstitutionDescription.objects.filter(lang=translation.get_language())
    a = models.HomeArticleEntry.objects.filter(lang=translation.get_language())
    q = models.QuoteEntries.objects.filter(lang=translation.get_language())
    v = models.VideoDesc.objects.filter(lang=translation.get_language())
    docs = models.DocumentEntries.objects.filter(lang=translation.get_language())
    ifirst = models.Institution.objects.first()
    icons = models.SupportedIcons.objects.all()
    
    inst_proj_entries = []
    if ifirst:
        inst_proj_entries = models.InstitutionProjectEntries.objects.filter(project__inst=ifirst.pk, lang=translation.get_language())
    
    context = {
        'blogs' : b,
        'inst' : i,
        'first_inst_proj_entries' : inst_proj_entries,
        'articles' : a,
        'quotes' : q,
        'videos' : v,
        'docs' : docs,
        'icons' : icons,
        'services' : models.ServiceEntries.objects.filter(lang=translation.get_language()) 
    }

    return HttpResponse(template.render(context, request))

@user_passes_test(decorators.admin_logged_in)
def store_admin_service(request):
    idb = int(request.POST.get('id',0))

    title_de = request.POST.get('title_de','')
    title_en = request.POST.get('title_en','')
    subtitle_de = request.POST.get('subtitle_de','')
    subtitle_en = request.POST.get('subtitle_en','')
    content_de = request.POST.get('content_de','')
    content_en = request.POST.get('content_en','')
    icon = request.POST.get('icon','')
    
    if idb == 0:
        serv = models.Service.objects.create(image_css=icon)
        models.ServiceEntries.objects.create(title=title_de, subtitle=subtitle_de, content=content_de, service=serv, lang="de")
        models.ServiceEntries.objects.create(title=title_en, subtitle=subtitle_en, content=content_en, service=serv, lang="en")
    else:
        serv = models.Service.objects.filter(pk=idb)
        serv.update(image_css=icon)
        serv = serv.first()
        models.ServiceEntries.objects.filter(lang="de", service=serv).update(title=title_de, subtitle=subtitle_de, content=content_de)
        models.ServiceEntries.objects.filter(lang="en", service=serv).update(title=title_en, subtitle=subtitle_en, content=content_en)

    title = (title_de, title_en)[translation.get_language() == 'de']
    json = {"id" :  str(serv.pk) , "title" : title , "changed" :  format_date(serv.changed) }
    return JsonResponse(json)
        
@user_passes_test(decorators.admin_logged_in)
def store_admin_article(request):
    idb = int(request.POST.get('id',0))

    title_de = request.POST.get('title_de','')
    title_en = request.POST.get('title_en','')
    subtitle_de = request.POST.get('subtitle_de','')
    subtitle_en = request.POST.get('subtitle_en','')
    content_de = request.POST.get('content_de','')
    content_en = request.POST.get('content_en','')
        
    fname = ""
    if "article_fname" in request.session:
        fname = request.session["article_fname"]
        del request.session["article_fname"]
        

    if idb == 0:
        art = models.HomeArticle.objects.create(image=fname)
        models.HomeArticleEntry.objects.create(title=title_de, shortdesc=subtitle_de, content=content_de, article=art, lang="de")
        models.HomeArticleEntry.objects.create(title=title_en, shortdesc=subtitle_en, content=content_en, article=art, lang="en")  
    else:
        art = models.HomeArticle.objects.filter(pk=idb)
        if fname != "":
            art.update(image=fname)
        art = art.first()
        models.HomeArticleEntry.objects.filter(article=art, lang="de").update(title=title_de, shortdesc=subtitle_de, content=content_de) 
        models.HomeArticleEntry.objects.filter(article=art, lang="en").update(title=title_en, shortdesc=subtitle_en, content=content_en)
                    
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = {"id" :  str(art.pk) , "title" :  title  , "changed" :  format_date(art.changed) , "image" :  fname }
    return JsonResponse(json)
 
@user_passes_test(decorators.admin_logged_in)              
def store_admin_blog(request):
    idb = int(request.POST.get('id',0))
    title_de = request.POST.get('title_de','')
    title_en = request.POST.get('title_en','')
    subtitle_de = request.POST.get('subtitle_de','')
    subtitle_en = request.POST.get('subtitle_en','')
    content_de = request.POST.get('content_de','')
    content_en = request.POST.get('content_en','')
        
    fname = ''
    if "blog_fname" in request.session:
        fname = request.session["blog_fname"]
        del request.session["blog_fname"]
        
    if idb == 0:
        b = models.Blog.objects.create(image=fname)
        models.BlogEntry.objects.create(title=title_de, subtitle=subtitle_de, content=content_de, blog=b, lang="de")
        models.BlogEntry.objects.create(title=title_en, subtitle=subtitle_en, content=content_en, blog=b, lang="en")  
    else:
        b = models.Blog.objects.filter(pk=idb) 
        if fname != '':
            b.update(image=fname)
        b = b.first()
        models.BlogEntry.objects.filter(blog=b, lang="de").update(title=title_de, subtitle=subtitle_de, content=content_de)
        models.BlogEntry.objects.filter(blog=b, lang="en").update(title=title_en, subtitle=subtitle_en, content=content_en)
            
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = {"id" : str(b.pk) , "title" : title, "changed" :  formate_date(b.changed) , "image" :  fname }
    return JsonResponse(json)

@user_passes_test(decorators.admin_logged_in)
def store_admin_inst(request):
    idb = int(request.POST.get('id',0))
    
    name_de = request.POST.get('name_de','')
    loc_name_de = request.POST.get('loc_name_de','')
    name_en = request.POST.get('name_en','')
    loc_name_en = request.POST.get('loc_name_en','')
  
    try:
        lng = Decimal(request.POST.get('lng','0.0'))
        lat = Decimal(request.POST.get('lat','0.0'))
    except:
        lng = 0
        lat = 0
    url = request.POST.get('url','')
    content_de = request.POST.get('content_de','')    
    content_en = request.POST.get('content_en','')

    fname = ""
    img_width = 0
    img_height = 0
    if "inst_fname" in request.session:
        fname = request.session["inst_fname"]
        del request.session["inst_fname"]
        im = Image.open(settings.IMG_DIR + fname)
        img_width, img_height = im.size
    
    if idb == 0:        
        inst = models.Institution.objects.create(lng=lng, lat=lat, link=url, image=fname, img_width=img_width, img_height=img_height)
        models.InstitutionDescription.objects.create(name=name_de, loclabel=loc_name_de, desc=content_de, lang='de', inst=inst)
        models.InstitutionDescription.objects.create(name=name_en, loclabel=loc_name_en, desc=content_en, lang='en', inst=inst)   
    else:
        inst = models.Institution.objects.filter(pk=idb)
        if fname != "":
            inst.update(image=fname,img_width=img_width, img_height=img_height)
        
        inst.update(lng=lng, lat=lat, link=url)
        inst = inst.first()
        models.InstitutionDescription.objects.filter(lang='de', inst=inst).update(name=name_de, loclabel=loc_name_de, desc=content_de)
        models.InstitutionDescription.objects.filter(lang='en', inst=inst).update(name=name_en, loclabel=loc_name_en, desc=content_en)
                    
    name = (name_de, name_en)[translation.get_language() == 'de']
    json = {"id" : str(inst.pk) , "name" :  name , "changed" :  format_date(inst.changed)  , "image" :  fname }
    return JsonResponse(json) 

@user_passes_test(decorators.admin_logged_in)
def store_admin_inst_proj(request):
    idb = int(request.POST.get('id',0))

    inst_id = request.POST.get('inst_id',0)
    title_de = request.POST.get('title_de','')
    title_en = request.POST.get('title_en','')
    content_de = request.POST.get('content_de','')
    content_en = request.POST.get('content_en','')
    if idb == 0:
        p = models.InstitutionProject.objects.create(inst=models.Institution.objects.get(pk=inst_id))
        models.InstitutionProjectEntries.objects.create(title=title_de, desc=content_de, lang='de', project=p)
        models.InstitutionProjectEntries.objects.create(title=title_en, desc=content_en, lang='en', project=p)        
    else:
        p = models.InstitutionProject.objects.get(pk=idb)
        models.InstitutionProjectEntries.objects.filter(lang='de', project=p).update(title=title_de, desc=content_de)
        models.InstitutionProjectEntries.objects.filter(lang='en', project=p).update(title=title_en, desc=content_en)
                
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = {"id" :  str(p.pk) , "title" :  title , "changed" : format_dat(p.changed)}
    return JsonResponse(json) 

@user_passes_test(decorators.admin_logged_in)
def store_admin_quote(request):
    idb = int(request.POST.get('id',0))
 
    role_de = request.POST.get('role_de','')
    role_en = request.POST.get('role_en','')
    content_de = request.POST.get('content_de','')
    content_en = request.POST.get('content_en','')
    name = request.POST.get('name','')
    
    fname = ""
    if "quote_fname" in request.session:
        fname = request.session["quote_fname"]
        del request.session["quote_fname"]
    
    
    if idb == 0:
        q = models.Quote.objects.create(name=name, image=fname)
        models.QuoteEntries.objects.create(content=content_de, role=role_de, lang='de', quote=q)
        models.QuoteEntries.objects.create(content=content_en, role=role_en, lang='en', quote=q)
    else:
        q = models.Quote.objects.filter(pk=idb)
        q.update(name=name)
        q = q.first()
        models.QuoteEntries.objects.filter(lang='de', quote=q).update(content=content_de, role=role_de)
        models.QuoteEntries.objects.filter(lang='en', quote=q).update(content=content_en, role=role_en)
        
    json = {"id" :  str(q.id) , "name" :  name , "changed" : date_format(q.changed) , "image" :  fname }
    return JsonResponse(json) 

@user_passes_test(decorators.admin_logged_in)
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
        d = models.Document.objects.create(icon=icon)
        models.DocumentEntries.objects.create(title=title_de, desc=desc_de, content=content_de, doc=d, lang='de')
        models.DocumentEntries.objects.create(title=title_en, desc=desc_en, content= content_en, doc=d, lang='en')
    else:
        d = models.Document.objects.filter(pk=idb)
        d.update(icon=icon)
        d = d.first()
        models.DocumentEntries.objects.filter(doc=d, lang='de').update(title=title_de, desc=desc_de, content=content_de)
        models.DocumentEntries.objects.filter(doc=d, lang='en').update(title=title_en, desc=desc_en, content= content_en)
        
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = {"id" : str(d.pk) , "title" : title , "changed" : format_date(d.changed)}
    return JsonResponse(json)     
    
@user_passes_test(decorators.admin_logged_in)   
def store_admin_video(request):
    idb = int(request.POST.get('id',0))
    vid = request.POST.get('vid','')
    title_de = request.POST.get('title_de','')
    title_en = request.POST.get('title_en','')
    content_de = request.POST.get('content_de','')
    content_en = request.POST.get('content_en','')
    if idb == 0:
        v = models.Video.objects.create(vid = vid)
        models.VideoDesc.objects.create(title=title_de, desc=content_de, lang='de', video=v)
        models.VideoDesc.objects.create(title=title_en, desc=content_en, lang='en', video=v)    
    else:
        v = models.Video.objects.filter(pk=idb)
        v.update(vid=vid)
        v = v.first()
        models.VideoDesc.objects.filter(lang='de', video=v).update(title=title_de, desc=content_de)
        models.VideoDesc.objects.filter(lang='en', video=v).update(title=title_en, desc=content_en)    
    
    title = (title_de, title_en)[translation.get_language() == 'de']
    json = {"id" : str(v.pk) , "title" :  title + ' (' + vid + ')' , "changed" : format_date(v.changed)}
    return JsonResponse(json)     

'''
is called when another institution is selected in the institution/project area
'''
@user_passes_test(decorators.admin_logged_in)
def change_admin_inst_proj(request):
    idb = request.POST.get('id',0)
    ipe = models.InstitutionProjectEntries.objects.filter(project__inst__pk=idb, lang=translation.get_language())

    js = serializers.serialize('json',ipe)
    return HttpResponse(js, content_type="application/json")    

@user_passes_test(decorators.admin_logged_in)
def change_admin_quote_selection(request):
    idb = request.POST.get('id',0)
    qe = models.QuoteEntries.objects.filter(quote=idb)
    q = models.Quote.objects.filter(pk=idb)
    data = list(chain(q, qe))
    data = serializers.serialize('json',data)
    return HttpResponse(data, content_type="application/json")   

'''
is called when the project entries should be changed in the institution/project area
'''
@user_passes_test(decorators.admin_logged_in)
def change_admin_inst_proj_selection(request):
    idb = request.POST.get('id',0)
    ipe = models.InstitutionProjectEntries.objects.filter(project__pk=idb)
    js = serializers.serialize('json',ipe)
    return HttpResponse(js, content_type="application/json")  

@user_passes_test(decorators.admin_logged_in)
def change_admin_doc_selection(request):
    idb = request.POST.get('id',0)
    d = models.Document.objects.filter(pk=idb)
    de = models.DocumentEntries.objects.filter(doc=idb)
    
    data = list(chain(d, de))
    data = serializers.serialize('json', data)
    return HttpResponse(data, content_type="application/json")

@user_passes_test(decorators.admin_logged_in)
def change_admin_service_selection(request):
    idb = request.POST.get('id',0)
    s = models.Service.objects.filter(pk=idb)
    se = models.ServiceEntries.objects.filter(service=idb)
    data = list(chain(s, se))
    data = serializers.serialize('json', data)
    return HttpResponse(data, content_type="application/json")

@user_passes_test(decorators.admin_logged_in)
def change_admin_video_selection(request):
    idb = request.POST.get('id',0)
    v = models.Video.objects.filter(pk=idb)
    ve = models.VideoDesc.objects.filter(video__pk=idb)
    data = list(chain(v, ve))
    data = serializers.serialize('json', data)
    return HttpResponse(data, content_type="application/json")

@user_passes_test(decorators.admin_logged_in)
def change_admin_article(request):
    idb = request.POST.get('id',0)
    be = models.HomeArticleEntry.objects.filter(article=idb)
    b = models.HomeArticle.objects.filter(pk=idb)
    data = list(chain(b, be))
    data = serializers.serialize('json', data)
    return HttpResponse(data, content_type="application/json")

@user_passes_test(decorators.admin_logged_in)
def delete_admin_service(request):
    idb = request.POST.get('id',0)
    models.Service.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

@user_passes_test(decorators.admin_logged_in)
def delete_admin_article(request):
    idb = request.POST.get('id',0)
    models.HomeArticle.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

@user_passes_test(decorators.admin_logged_in)
def delete_admin_projinst(request):
    idb = request.POST.get('id',0)
    models.InstitutionProject.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")
  
@user_passes_test(decorators.admin_logged_in)  
def delete_admin_quote(request):
    idb = request.POST.get('id',0)
    models.Quote.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

@user_passes_test(decorators.admin_logged_in)
def delete_admin_doc(request):
    idb = request.POST.get('id',0)
    models.Document.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

@user_passes_test(decorators.admin_logged_in)
def delete_admin_video(request):
    idb = request.POST.get('id',0)
    models.Video.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

def get_inst_projects(request):
    idb = request.POST.get('id',0)
    entr = models.InstitutionProjectEntries.objects.filter(project__inst=idb, lang=translation.get_language())
    js = serializers.serialize('json',entr)
    return HttpResponse(js, content_type="application/json")  

'''
Find a Blog Entry and return as json
This special task is necessary because joined tables cannot be fully serialized as json
'''
def get_blog(request):
    idb = request.POST.get('id',0)
    be = models.BlogEntry.objects.filter(blog=idb, lang=translation.get_language())
    js = serializers.serialize('json',be)
    return HttpResponse(js, content_type="application/json")  

def get_blog_entry(idb):
    be = models.BlogEntry.objects.filter(blog=idb)
    b = models.Blog.objects.filter(pk=idb)
    combined = list(chain(b, be))
    return serializers.serialize('json', combined)

@user_passes_test(decorators.admin_logged_in)
def change_admin_blog(request):
    idb = request.POST.get('id',0)
    data = get_blog_entry(idb)  
    return HttpResponse(data, content_type="application/json")

@user_passes_test(decorators.admin_logged_in)    
def delete_admin_blog(request):
    idb = request.POST.get('id',0)
    models.Blog.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

@user_passes_test(decorators.admin_logged_in)
def delete_admin_inst(request):
    idb = request.POST.get('id',0)
    models.Institution.objects.filter(pk=idb).delete()
    return HttpResponse("ok", content_type="text/plain")

'''
Find a Institution Entry and return as json
This special task is necessary because joined tables cannot be fully serialized as json
'''
def get_inst_entry(idb):
    be = models.InstitutionDescription.objects.filter(inst=idb)
    b = models.Institution.objects.filter(pk=idb)
    combined = list(chain(b, be))
    return serializers.serialize('json', combined)

@user_passes_test(decorators.admin_logged_in) 
def change_admin_inst(request):   
    idb = request.POST.get('id',0)
    data = get_inst_entry(idb)  
    return HttpResponse(data, content_type="application/json")
    
def logout_process(request):
    ts.invalidate()
    del request.session['user']
    request.session.modified = True
    logout(request)
    return HttpResponseRedirect("index")
 
def login_process(request):
    e = request.POST.get('email','')
    p = request.POST.get('password','')
      
    try:
        curr_user = ts.login(e,p)
        if not (curr_user is None):
            User.objects.filter(username=e).delete()
            user = User.objects.create_user(curr_user['userName'], curr_user['email'], p, is_superuser = True, first_name=curr_user['firstname'], last_name= curr_user['lastname'])
            user.save()
            #user = authenticate(username=u, password=p) 
            
            login(request, user)
        request.session['user'] = curr_user
        request.session.modified = True 
    except Exception as e:
        logger.warning ("logint failed:" + str(e))
        messages.warning(request, "login_failed")
     
    return HttpResponseRedirect("index")

def register_process(request):
    user = request.POST.get('user')
    pw = request.POST.get('pw')
    pw_again = request.POST.get('pw_again')
    firstName = request.POST.get('firstName')
    lastName = request.POST.get('lastName')
    #     orcid = request.POST.get('orcid')
    gender = request.POST.get('gender')
    
    recaptcha_response = request.POST.get('g-recaptcha-response')
    data = {
       'secret': settings.RECAPTCHA_KEY_SECRET,
       'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    if result['success']:
        logger.info('success')
        #res = ts.register(request)
        #logger.info(res)
    else:
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
    phone = request.POST.get('phone','')
    message = request.POST.get('message','')
    message += "email:" + email
    send_mail('website message', message, 'albert.greinoecker@gmail.com', ['albert.greinoecker@gmail.com'], fail_silently=False,
)
    
            
# ############################################################
# Services
# ############################################################

@user_passes_test(decorators.admin_logged_in)
def upload_img(request):
    file = request.FILES['file']
    type = request.POST.get('type')
    #blog_id = request.POST.get('blog_id')
    fname = str(uuid.uuid4()) + "." + os.path.splitext(str(file))[1][1:].strip() 
    path = default_storage.save(settings.IMG_DIR + fname, ContentFile(file.read()))
    request.session[type + "_fname"] = fname
    request.session.modified = True
    
    return HttpResponse(json.dumps(fname), content_type="application/json") 

# ############################################################
# Utils
# ############################################################

def format_date(f):
    return f.strftime('(%d/%m/%Y)')
