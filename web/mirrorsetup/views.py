from django.shortcuts import render
from django.conf import settings as conf_settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound,JsonResponse
import os, json
import logging
import socket

logger = logging.getLogger('django.mirrorsetup')

def home(request):
    if request.method == "POST":
        return HttpResponseForbidden()
    return render(request, 'mirrorsetup/home.html')

def intro(request):
    if request.method == "POST":
        return HttpResponseForbidden()
    return render(request, 'mirrorsetup/intro.html')

@login_required
def setup(request):
    with open(f'{conf_settings.HOME_DIR}{os.sep}widgets.json', encoding='utf-8') as widgets_config_file:
        WIDGETS_CONFIG = json.load(widgets_config_file)
    context = {
        "widgets": WIDGETS_CONFIG
    }
    return render(request, 'mirrorsetup/setup.html', context=context)

@login_required
def apply(request):
    widgets_json = request.POST.get('widgets')
    widgets = json.loads(widgets_json)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 9086))
    sock.send(widgets_json.encode('utf-8'))
    sock.close()

    data = {
            "status": True,
                }
    try:        
        return JsonResponse(data)
    except Exception as exc:
        logger.exception('Cannot return status JSON response')

@login_required
def cancel(request):
    return render(request, 'mirrorsetup/setup.html')

@login_required
def widget_settings(request):
    try:
        widget_name = request.GET.__getitem__('widget')
        with open(f'{conf_settings.HOME_DIR}{os.sep}widgets.json', encoding='utf-8') as widgets_config_file:
            WIDGETS_CONFIG = json.load(widgets_config_file)
        context = WIDGETS_CONFIG[widget_name]
        return render(request, 'mirrorsetup/widget_settings.html', context=context)
    except Exception as exc:
        logger.exception('Cannot process widget settings request!')
