import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse

def does_login_with_cookie_work(request):
    return render(request, template_name='sandbox/does-login-with-cookie-work.html')

def transcribe_application(request):
    return render(request, template_name='sandbox/transcribe.html')

def __transcribe_application(request):

    # from user_agents import parse

    USER_AGENTS = {
        'Mozilla': 38,
        'Safari': 8,
        'Chrome': 40,
        'IE': float('inf'),
        'Opera': 47
    }

    ua_string = request.META['HTTP_USER_AGENT']
    user_agent = parse(ua_string)

    browser = user_agent.browser

    required_version = USER_AGENTS.get(browser.family)

    # NOTE:  this is somewhat dubious ...
    if required_version is None:
        logging.warn("Unknown user agent %s", user_agent)
        return render(request, template_name='sandbox/transcribe.html')

    actual_version, *_ = browser.version

    if actual_version < required_version:
        # return render(request, template_name='sandbox/browser-update.html')
        return redirect('sandbox:browser-update')

    return render(request, template_name='sandbox/transcribe.html')

def index(request):
    context = {
        'tests': [
            {
                'title': 'Reichsgericht I._ZvS_1902_4.Q_duplicated',
                'collection': 2305,
                'document': 38115,
                'pages': list(range(1, 9 + 1))
            },
            {
                'title': 'HTR Bentham Box 35_duplicated',
                'collection': 2305,
                'document': 31902,
                'pages': list(range(1, 8 + 1))
            },
            {
                'title': 'Arabic test pages',
                'collection': 2305,
                'document': 26455,
                'pages': list(range(1, 3 + 1))
            },
            {
                'title': 'ABP_Malgersdorf_vor_1600_duplicated',
                'collection': 2305,
                'document': 23315,
                'pages': list(range(1, 10 + 1))
            },
            {
                'title': 'DEMO_Liber Extended M8_duplicated',
                'collection': 2305,
                'document': 23220,
                'pages': list(range(1, 4 + 1))
            },
            {
                'title': '03178_duplicated',
                'collection': 2305,
                'document': 35018,
                'pages': list(range(1, 2 + 1))
            },
            {
                'title': 'DEMO_StazH_Protokolle_t2i_duplicated',
                'collection': 2305,
                'document': 23219,
                'pages': list(range(1, 9 + 1))
            },
            {
                'title': 'DEMO_Österr. Bibelübersetzer M3_duplicated',
                'collection': 2305,
                'document': 23218,
                'pages': list(range(1, 7 + 1))
            },
            {
                'title': 'DEMO_Realkatalog M1_duplicated',
                'collection': 2305,
                'document': 23217,
                'pages': list(range(1, 23 + 1))
            },
            {
                'title': 'IMAGES',
                'collection': 2305,
                'document': 4949,
                'pages': list(range(1, 4 + 1))
            }
        ]
    }
    return render(request, template_name='sandbox/index.html', context=context)

from django.views import View
class SettingsDialog(View):

    template_name = 'sandbox/settings-dialog.html'

    # def get_context_data(self, **kwargs):
    #     context = super(SettingsDialog, self).get_context_data(**kwargs)
    #     return context

    def post(self, request, *args, **kwargs):

        from django.http import HttpResponseRedirect
        if request.is_ajax():
            return HttpResponse(501)

        if not request.user.is_authenticated:
            from . import models
            settings_id = request.session.get('settings', None)
            if settings_id is not None:
                settings = models.Settings.objects.get(id=settings_id)
            else:
                settings = models.Settings()
        elif not request.user.settings:
            settings = models.Settings(owner=request.user)
        else:
            settings = request.user.settings

        if settings is None:
            settings = models.Settings(owner=request.user)

        from . import forms
        form = forms.SettingsForm(request.POST, instance=settings)

        if not form.is_valid():
            from django.http import HttpResponse
            print(form.errors.as_data())
            return HttpResponse(400)

        form.save()

        if not request.user.is_authenticated:
            request.session['settings'] = settings.id

        from django.urls import reverse
        return HttpResponseRedirect(reverse('sandbox:settings-dialog', *args, **kwargs))

    def get(self, request, *args, **kwargs):

        from django.http import JsonResponse, HttpResponse
        from . import models

        if not request.user.is_authenticated:
            settings_id = request.session.get('settings', None)
            if settings_id is not None:
                settings = models.Settings.objects.get(id=settings_id)
            else:
                settings = models.Settings() # defaults ...
        else:
            settings = request.user.settings

        if not request.is_ajax():
            from . import forms
            context = {
                'form': forms.SettingsForm(instance=settings),
                'settings': settings
            }
            return render(request, template_name=self.template_name, context=context)
            # return HttpResponse(501)

        return JsonResponse({
            'layout': {
                'isHorizontal': settings.is_layout_horizontal,
                'isReversed': settings.is_layout_reversed,
                'extent': settings.layout_extent
            }
        })

def viewer(request, name, col_id, doc_id, page_nr):
    context = {'viewer': name}
    return render(request, template_name='sandbox/viewer.html', context=context)

def manager(request):
    return render(request, template_name='sandbox/manager.html')

def zoom(request, demo_name=None):
    templates = {
        'kiss': 'kiss',
        'kiss2': 'kiss2',
        'kiss3': 'kiss3',
        'win95': 'win95',
        'demo_name': 'demo-name.html',
    }
    template = templates.get(demo_name, 'index.html')
    return render(request, template_name='sandbox/demo/zoom/%s.html' % template)

def viewers(request, name):
    templates = {
        'layout': 'layout',
        'openlayers': 'openlayers'
    }
    template = templates.get(name, 'index.html')
    return render(request, template_name='sandbox/demo/viewers/%s.html' % template)

def matti(request):

    use_api = int(request.GET.get('api', 0))

    if use_api == 1:
        template_name = 'tagging2'
    else:
        template_name = 'tagging'

    return render(request, template_name='sandbox/matti/%s.html' % template_name)
