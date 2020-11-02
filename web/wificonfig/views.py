from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound,JsonResponse
from . import wifimanager
import json
import socket
import logging

logger = logging.getLogger('django.wifisetup')

@login_required
def status(request):
    if request.method == "POST":
        return HttpResponseForbidden()
    result, result2 = wifimanager.scanner()
    if result:
        context = {"status": True, "result": result, "connected": result2}
    else:
        context = {"status": False,}    
    return render(request, 'wificonfig/status.html', context=context)

@login_required
def update_hotspots_list(request):
    result, result2 = wifimanager.scanner()
    if result:
        data = {"status": True, "result": result, "connected": result2}
    else:
        data = {"status": False,} 
    return JsonResponse(data)

@login_required
def config(request):
    if request.method == "POST":
        return HttpResponseForbidden()
    ssid = request.GET.__getitem__('ssid')
    context = {
        'ssid': ssid
    }
    return render(request, 'wificonfig/config.html', context=context)

@login_required
def connect(request):
    """ Gets wifi credentials from provided by the user from the web interface."""
    wifi_json_credentials = request.POST.get('credentials')
    wifi_credentials = json.loads(wifi_json_credentials)

    if wifimanager.connect(wifi_credentials):
        data = {
            "status": True,
        }
    else:
        data = {
            "status": False,
        }

    try:        
        return JsonResponse(data)
    except Exception as exc:
        logger.exception('Cannot return status JSON response')