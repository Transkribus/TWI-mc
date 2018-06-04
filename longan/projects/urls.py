from django.conf.urls import url
from django.views.decorators.cache import cache_page

from transkribus.decorators import login_required 

from . import views

urlpatterns = [
    url(r'^(?P<slug_or_id>[\w-]+)/$', login_required(cache_page(60 * 5)(views.project_detail)), name='project-detail')
]
