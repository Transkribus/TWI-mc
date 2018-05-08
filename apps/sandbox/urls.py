from django.conf.urls import include, url
from django.views.generic import TemplateView

from . import views

urlpatterns = (
    url(r'^$', views.index, name='index'),
    url(r'^(?P<name>[a-z]+)/(?P<col_id>\d+)/(?P<doc_id>\d+)/(?P<page_nr>\d+)/$', views.viewer, name='viewer'),

    url(r'^does-login-with-cookie-work$', views.does_login_with_cookie_work, name='does-login-with-cookie-work'),
    url(r'^rtl/$', TemplateView.as_view(template_name='sandbox/rtl.html'), name='rtl'),

    url(r'^manager/$', views.manager, name='manager'), # thomas uses this

    url(r'^render/$', TemplateView.as_view(template_name='sandbox/render.html'), name='render'),

    url(r'^prototype/', include([

        url(r'^$', TemplateView.as_view(template_name='sandbox/prototype.html'), name='prototype'),

        url(r'^transcribe/$', views.transcribe_application, name='transcribe'),
        url(r'^browser-update/$', TemplateView.as_view(template_name='sandbox/browser-update.html'), name='browser-update'),

        url('^ui/', include([

            url('^components/', include([
                url(r'^svg-image-viewer/$', TemplateView.as_view(template_name='sandbox/svg-image-viewer.html'), name='svg-image-viewer'),
                url(r'^plain-text-editor/$', TemplateView.as_view(template_name='sandbox/plain-text-editor.html'), name='plain-text-editor'),
                url(r'^xml-editor/$', TemplateView.as_view(template_name='sandbox/xml-editor.html'), name='xml-editor'),
            ])),

            url('^dialogs/', include([
                url(r'^login-dialog/$', TemplateView.as_view(template_name='sandbox/objects/login-dialog.html'), name='login-dialog'),
                url(r'^settings-dialog/$', views.SettingsDialog.as_view(), name='settings-dialog'),
                url(r'^character-table/$', TemplateView.as_view(template_name='sandbox/character-table.html'), name='character-table'),                
            ])),

            url('^widgets/', include([

                url(r'^loader/$', TemplateView.as_view(template_name='sandbox/loader.html'), name='loader'),
                url(r'^toolbar/$', TemplateView.as_view(template_name='sandbox/toolbar.html'), name='toolbar'),

                url(r'^zoomable/$', TemplateView.as_view(template_name='sandbox/zoomable.html'), name='zoomable'),

                url(r'^layout/$', TemplateView.as_view(template_name='sandbox/layout.html'), name='layout'),
                url(r'^text-manager/$', TemplateView.as_view(template_name='sandbox/text-manager.html'), name='text-manager'),

            ])),

        ])),

        url('^models/', include([
            url(r'^current-transcript/$', TemplateView.as_view(template_name='sandbox/current-transcript.html'), name='current-transcript'),
        ])),
        
        url('^experimental/', include([
            url(r'^text-viewer/$', TemplateView.as_view(template_name='sandbox/text-viewer.html'), name='text-viewer'),
            url(r'^wysiwyg-editor/$', TemplateView.as_view(template_name='sandbox/wysiwyg-editor.html'), name='wysiwyg-editor'),
            url(r'^tag-editor/$', TemplateView.as_view(template_name='sandbox/tag-editor.html'), name='tag-editor'),
            url(r'^layout-with-overlay/$', TemplateView.as_view(template_name='sandbox/layout-with-overlay.html'), name='layout-with-overlay'),
            url(r'^contenteditable/', include([
                url(r'^line-list/$', TemplateView.as_view(template_name='sandbox/purgatory.html'), name='purgatory'),
                url(r'^beak/$', TemplateView.as_view(template_name='sandbox/desecration.html'), name='desecration'),
                url(r'^caret/$', TemplateView.as_view(template_name='sandbox/abyss.html'), name='abyss')
            ])),

        ])),

        url(r'^parsers/$', TemplateView.as_view(template_name='sandbox/parsers.html'), name='parsers'),

    ])),


    url(r'^api/', include([
        url('^save/$', TemplateView.as_view(template_name='sandbox/api/save.html'), name='save')
    ], namespace='api')),

    url(r'^test/$', TemplateView.as_view(template_name='sandbox/test.html'), name='test'),

    url(r'^demo/', include([
        url(r'^text-editor/$', TemplateView.as_view(template_name='sandbox/demo/text-editor.html'), name='text-editor'),
        url(r'^render/$', TemplateView.as_view(template_name='sandbox/demo/render-with-table.html'), name='render-with-table'),
        url(r'^transcriber/$', TemplateView.as_view(template_name='sandbox/demo/transcriber.html'), name='transcriber'),
        url(r'^review/$', TemplateView.as_view(template_name='sandbox/demo/line_review.html'), name='line-review'),
        url(r'^viewers/([^/]+)/$', views.viewers, name='viewers'),
        url(r'^zoom/([^/]+)/$', views.zoom, name='zoom'),
    ])),

    url(r'^utils/$', TemplateView.as_view(template_name='sandbox/utils.html'), name='utils'),

    url(r'^matti/', include([
        url(r'^tagging/$', views.matti, name='tagging'),
    ], namespace='matti')),

    url(r'^nathanael/', include([
        url(r'^custom-attr/$', TemplateView.as_view(template_name='sandbox/nathanael/custom-attr.html'), name='custom-attr'),
        url(r'^page-tests/$', TemplateView.as_view(template_name='sandbox/nathanael/page-tests.html'), name='custom-attr'),
    ], namespace='nathanael')),

)
