from django.shortcuts import render, redirect
from maestor.models import Disk, Server, SmartReport, Attribute, WarningCriteria, IOStat, Flag, DiskFlag, FlagRange
import datetime
def index(request):
    if request.user.is_authenticated():
        return redirect('home')
    context = {}
    return render(request, 'maestor/index.html', context)

def home(request):
    context={'flags':DiskFlag.objects.all()}
    return render(request, 'maestor/home.html', context)

def servers(request):
    context = {}
    context['servers'] = Server.objects.all()
    return render(request, 'maestor/servers.html', context)

def server_disks(request,server):
    server = Server.objects.get(pk=server)
    context = {}
    context['server'] = server
    return render(request, 'maestor/server_disks.html', context)

def model_disks(request):
    model = request.GET.get('model',None)
    firmware = request.GET.get('firmware',None)
    query = {'model':model} 
    if firmware is not None:
        query['firmware']=firmware 
    disks = Disk.objects.filter(**query)
    context = {'disks':disks,'model':model,'firmware':firmware}
    return render(request, 'maestor/model_disks.html', context)

def disk_details(request,disk):
    disk = Disk.objects.get(pk=disk)
    context = {}
    context['disk'] = disk
    return render(request, 'maestor/disk_details.html', context)

def smart_report_body(request,smart_report):
    smart_report = SmartReport.objects.get(pk=smart_report)
    context = {}
    context['smart_report'] = smart_report
    return render(request, 'maestor/smart_report_body.html', context)
