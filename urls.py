from django.conf.urls import include, url

from . import views

urlpatterns = [
 
    url(r'^table_ajax/(?P<list_name>[a-z]+)$', views.table_ajax, name='table_ajax'),
    url(r'^table_ajax/(?P<list_name>[a-z]+)/(?P<collId>[0-9]+)$', views.table_ajax, name='table_ajax'),
    url(r'^table_ajax/(?P<list_name>[a-z]+)/(?P<collId>[0-9]+)/(?P<docId>[0-9]+)$', views.table_ajax, name='table_ajax'),
    url(r'^table_ajax/u/(?P<userId>[0-9]+)/(?P<list_name>[a-z]+)$', views.table_ajax, name='table_ajax'),

    url(r'^table_ajax_public/(?P<list_name>[a-z]+)$', views.table_ajax_public, name='table_ajax_public'),
 
    url(r'^thumb/(?P<collId>[0-9]+)$', views.collection_thumb, name='collection_thumb'),
    url(r'^thumb/(?P<collId>[0-9]+)/(?P<docId>[0-9]+)$', views.document_thumb, name='document_thumb'),


]
