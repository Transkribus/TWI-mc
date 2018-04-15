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
    url(r'^upload_img', v.upload_img, name='upload_img'),
    url(r'^change_admin_blog', v.change_admin_blog, name='change_admin_blog'),
    url(r'^delete_admin_blog', v.delete_admin_blog, name='delete_admin_blog'),
    url(r'^blog_detail', v.blog_detail, name='blog_detail'),
    url(r'^store_admin_inst', v.store_admin_inst, name='store_admin_inst'),
    url(r'^delete_admin_inst', v.delete_admin_inst, name='delete_admin_inst'),
    url(r'^change_admin_inst', v.change_admin_inst, name='change_admin_inst'),
    url(r'^store_admin_proj', v.store_admin_inst_proj, name='store_admin_inst_proj'),
    url(r'^change_admin_proj', v.change_admin_inst_proj, name='change_admin_inst_proj'),
    url(r'^change_admin_pr_inst_selection', v.change_admin_inst_proj_selection, name='change_admin_inst_proj_selection'),
    url(r'^inst_detail', v.inst_detail , name='inst_detail'),
    url(r'^store_admin_article', v.store_admin_article , name='store_admin_article'),
    url(r'^home_article_details', v.home_article_details , name='home_article_details'),
    url(r'^store_admin_quote', v.store_admin_quote , name='store_admin_quote'),   
    url(r'^store_admin_video', v.store_admin_video , name='store_admin_video'),
    url(r'^change_admin_article', v.change_admin_article , name='change_admin_article'),
    url(r'^store_admin_doc', v.store_admin_doc , name='store_admin_doc'),
    url(r'^change_admin_quote_selection', v.change_admin_quote_selection , name='change_admin_quote_selection'),
    url(r'^change_admin_doc_selection', v.change_admin_doc_selection , name='change_admin_doc_selection'),
    url(r'^change_admin_video_selection', v.change_admin_video_selection , name='change_admin_video_selection')
]
