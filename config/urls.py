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
from django.contrib.auth.views import LogoutView

from transkribus.views import LoginWithCookieView

urlpatterns = [

    url(r'^', include('home.urls', namespace='home')),
    # url(r'^home/', include('home.urls', namespace='home')),
    url(r'^sandbox/', include('sandbox.urls', namespace='sandbox')),

    url(r'^library/', include('library.urls', namespace='library')),
    url(r'^projects/', include('projects.urls', namespace='projects')),
    url(r'^admin/', admin.site.urls),

    url(r'^edit/', include('edit.urls', namespace='edit')),

    # accounts
    url('logout/', LogoutView.as_view(), name='logout'),
    url('^login/$', LoginWithCookieView.as_view(template_name='registration/login-with-cookie.html'), name='login'),

    # url(r'^search/', include('search.urls', app_name='search', namespace='search')),
    # url(r'^view/', include('edit.urls', app_name='edit', namespace='edit')),
    # url(r'^edit/', include('edit.urls', app_name='edit', namespace='edit')),
    # url(r'^utils/', include('utils.urls', app_name='utils', namespace='utils')),
    # url(r'^dashboard/', include('apps.dashboard.urls', app_name='dashboard', namespace='dashboard')),

    # url(r'^register$', apps.utils.views.register, name='register'),
    # url(r'^logout/$', apps.utils.views.logout_view, name='logout'),

    # url(r'^register$', apps.utils.views.register, name='register'),
    # url(r'^admin/', admin.site.urls),
    # url('', include('django.contrib.auth.urls')),

    url(r'^i18n/', include('django.conf.urls.i18n')),

]
