"""mc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

import apps.utils.views
import mc.views
import settings

from apps import transkribus

from apps.transkribus import views
urlpatterns = [
    ##Pass on to app urls.py##
    #this causes various fails for some reason, though it would be nice to pass in app_name to library....
#    url(r'^library/', include('library.urls')),
#    url(r'^review/', include('review.urls')),
    #index is dashboard for now

    # apps/urls.py ##
    # url(r'^dashboard/', include('apps.dashboard.urls', app_name='dashboard', namespace='dashboard')),
    url(r'^library/', include('apps.library.urls', app_name='library', namespace='library')),
    url(r'^search/', include('apps.search.urls', app_name='search', namespace='search')),
    url(r'^view/', include('apps.edit.urls', app_name='edit', namespace='edit')),
    url(r'^edit/', include('apps.edit.urls', app_name='edit', namespace='edit')),
    url(r'^utils/', include('apps.utils.urls', app_name='utils', namespace='utils')),
    url(r'^projects/', include('apps.projects.urls', app_name='projects', namespace='projects')),
    url(r'^sandbox/', include('apps.sandbox.urls', app_name='sandbox', namespace='sandbox')),

    ## Project pages for My collection ##
    url(r'^$', mc.views.index, name='index'),
    url(r'^about/$', mc.views.about, name='about'),
    url(r'^user_guide/$', mc.views.user_guide, name='user_guide'),
    url(r'^crowd/$', mc.views.crowd_howto, name='crowd_howto'),
    url(r'^release_notes/$', mc.views.release_notes, name='release_notes'),
    url(r'^browser_compat/$', mc.views.browser_compat, name='browser_compat'),

    ## Others ##
    url(r'^admin/', admin.site.urls),
    url(r'^register$', apps.utils.views.register, name='register'),
    # url(r'^logout/$', apps.utils.views.logout_view, name='logout'),
    url('^login/$', transkribus.views.LoginWithCookie.as_view(template_name='registration/login-with-cookie.html'), name='login-with-cookie'),
    url(r'^register$', apps.utils.views.register, name='register'),
    url(r'^admin/', admin.site.urls),
    url('', include('django.contrib.auth.urls')),

    url(r'^i18n/', include('django.conf.urls.i18n')),

]
