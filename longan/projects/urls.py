from django.conf.urls import url
from django.views.decorators.cache import cache_page

from transkribus.decorators import login_required 

from . import views

urlpatterns = [
    url(r'^$', views.ProjectListView.as_view(), name='project-list'),
    # url(r'^$', cache_page(3600 * 24)(views.ProjectListView.as_view()), name='project-list'),
    url(r'^(?P<slug_or_id>([\w-]+|\d+))/$', login_required(cache_page(60 * 5)(views.project_detail)), name='project-detail'),
    url(r'^(?P<id>\d+)/subscribe/$', login_required(views.subscribe_view), name='subscribe')
]
