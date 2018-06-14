from django.conf.urls import url, include
from django.views.generic.base import RedirectView

from apps.transkribus.decorators import login_required 

from . import views

urlpatterns = [

    url(r'^$', views.CollectionListView.as_view(), name='index'),

    url(r'^test/$', views.test, name='test'),

    url('^collections/', include([
        url(r'^$', views.CollectionListView.as_view(), name='collection-list'),
        url(r'^(?P<col_id>\d+)/$', views.CollectionDetailView.as_view(), name='collection-detail'),
        url(r'^(?P<col_id>\d+)/documents/', include([
            url('^$', views.DocumentListView.as_view(), name='document-list'),
            url(r'^(?P<doc_id>\d+)/$', views.DocumentDetailView.as_view(), name='document-detail'),
            url(r'^(?P<doc_id>\d+)/pages/$', views.PageListView.as_view(), name='page-list'),
        ]))
    ])),
    
    url(r'^(?P<col_id>\d+)/$', views.DocumentListView.as_view(), name='document-list--compat'),

    url(r'^projects/(?P<slug_or_id>[\w-]+)/$', RedirectView.as_view(
        pattern_name='projects:project-detail',
        permanent=True, query_string=True))

]
