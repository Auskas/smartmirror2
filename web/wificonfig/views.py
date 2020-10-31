from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound,JsonResponse
from . import wifimanager
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