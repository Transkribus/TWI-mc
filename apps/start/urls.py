from django.conf.urls import include, url

from . import views as v

urlpatterns = [
    url(r'^$', v.index, name='index'),
    url(r'^index$', v.index, name='index'),
    url(r'^start_admin', v.admin, name='fh_admin'),
    #url(r'^store_admin', v.store_admin, name='store_admin'),
    url(r'^store_admin_blog', v.store_admin_blog, name='store_admin_blog'),
    #url(r'^script', v.script, name='script'),
    url(r'^login$', v.login_process, name='login_process'),
    url(r'^logout$', v.logout_process, name='logout_process'),
    url(r'^change_lang', v.change_lang , name='change_lang'),
    url(r'^contact', v.contact , name='contact'),
    url(r'^register_process', v.contact , name='register_process'),
    url(r'^upload_blog_img', v.upload_blog_img, name='upload_blog_img'),
    url(r'^change_admin_blog', v.change_admin_blog, name='change_admin_blog')
]
