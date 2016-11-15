from django.conf.urls import include, url

from . import views

urlpatterns = [

    url(r'^$', views.collections, name='index'),
    url(r'^collections$', views.collections, name='collections'),
    url(r'^collection/([\-0-9]+)$', views.collection, name='collection'),
    url(r'^collection_noaccess/([\-0-9]+)$', views.collection_noaccess, name='collection_noaccess'),
    url(r'^document/([\-0-9]+)/([0-9]+)$', views.document, name='document'),
    url(r'^page/([\-0-9]+)/([0-9]+)/([0-9]+)$', views.page, name='page'),
    url(r'^transcript/([\-0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)$', views.transcript, name='transcript'),
    url(r'^region/([\-0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/([\w-]+)$', views.region, name='region'), #TODO improve regionId regex?
    url(r'^line/([\-0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/([\w-]+)/([\w-]+)$', views.line, name='line'), #TODO as above...
    url(r'^word/([\-0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/([\w-]+)/([\w-]+)/([\w-]+)$', views.word, name='word'), #TODO as above...
    url(r'^rand/([\-0-9]+)/(word|line|region|transcript|document)$', views.rand, name='rand'),

    url(r'^error$', views.error, name='error'),

    url(r'^users/([\-0-9]+)/([0-9]+)$', views.users, name='users'),
#    url(r'^register$', views.register, name='register'),
#    url(r'^profile$', views.profile, name='profile'),
#    url(r'^i18n/', include('django.conf.urls.i18n')),
    #url('^', include('django.contrib.auth.urls')),
]
