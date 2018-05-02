from django.conf.urls import url, include

from apps.transkribus.decorators import login_required 

from . import views

urlpatterns = [

    url(r'^$', views.CollectionListView.as_view(), name='index'),

    url(r'^test/$', views.test, name='test'),

    url('^collections/', include([
        url(r'^$', views.CollectionListView.as_view(), name='collection-list'),
        url(r'^(?P<col_id>\d+)/$', views.CollectionView.as_view(), name='collection-detail'),
        url(r'^(?P<col_id>\d+)/documents/', include([
            url('^$', views.DocumentListView.as_view(), name='document-list'),
            url(r'^(?P<doc_id>\d+)/$', views.DocumentView.as_view(), name='document-detail'),
            url(r'^(?P<doc_id>\d+)/pages/$', views.PageListView.as_view(), name='page-list'),
        ]))
    ])),
    
    url(r'^(?P<col_id>\d+)/$', views.DocumentListView.as_view(), name='document-list--compat'),


    url(r'^projects/(?P<slug>[\w-]+)/$', login_required(views.project_detail), name='project-detail'),

    url(r'^([\-0-9]+)/([0-9]+)/([0-9]+)$', views.document_page, name='document_page'),
    url(r'^([\-0-9]+)/([0-9]+)$', views.document_page, name='document_page'),
    # url(r'^([\-0-9]+)/([0-9]+)/([0-9]+)$', views.page, name='page'),
    url(r'^([\-0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)$', views.transcript, name='transcript'),
    url(r'^([\-0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/([\w-]+)$', views.region, name='region'), #TODO improve regionId regex?
    url(r'^([\-0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/([\w-]+)/([\w-]+)$', views.line, name='line'), #TODO as above...
    url(r'^([\-0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)/([\w-]+)/([\w-]+)/([\w-]+)$', views.word, name='word'), #TODO as above...
    url(r'^([\-0-9]+)/(word|line|region|transcript|document)$', views.rand, name='rand'),

    url(r'^users/([\-0-9]+)/([0-9]+)$', views.users, name='users'),
    url(r'^coll_metadata/(?P<collId>[0-9]+)$', views.collection_metadata, name='collection_metadata'),
    url(r'^doc_metadata/(?P<collId>[0-9]+)/(?P<docId>[0-9]+)$', views.document_metadata, name='document_metadata'),
]
