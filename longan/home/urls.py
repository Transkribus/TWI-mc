from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^user_guide/$', views.user_guide, name='user_guide'),
    url(r'^crowd/$', views.crowd_howto, name='crowd_howto'),
    url(r'^release_notes/$', views.release_notes, name='release_notes'),
    url(r'^browser_compat/$', views.browser_compat, name='browser_compat'),
]
