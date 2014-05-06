from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from auth import ServerAuth
from models import Server, Disk, SmartReport, Attribute
from parsers import SmartParse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

@api_view(['POST'])
@permission_classes((ServerAuth, ))  
def post_smart_report(request):
    server = request.DATA.get('server')
    body = request.DATA.get('body')
    unix_device = request.DATA.get('unix_device')
    
    server = Server.objects.get(name=server)
    parser = SmartParse(body,'6.2')
    
    try:
        server = Server.objects.get(name=server)
        parser = SmartParse(body,'6.2')
        
        try:
            disk = Disk.objects.get(pk=parser.get_pk())
        except ObjectDoesNotExist, e:
            disk = Disk(pk=parser.get_pk(),server=server,unix_device=unix_device,**parser.info)
            disk.save()
        SM = SmartReport(disk=disk,server=server,firmware=parser.info['firmware'],text=body,parsed=datetime.now(),ip=request.META['REMOTE_ADDR'])
        SM.save()
        for attr in parser.attrs:
            a = Attribute(smart_report=SM,name=attr['name'],value=attr['value'],worst=attr['worst'],thresh=attr['thresh'],failed=attr['failed'],raw_value=attr['raw_value'])
            a.save()
#         Disk.objects.create()
        return Response({'info':parser.info,'attrs':parser.attrs,'pk':parser.get_pk()})
    except Exception, e:
        return Response({'status':'failed','message':e.message})
    
    return Response({'status':'success'})

@api_view(['GET'])
@permission_classes((ServerAuth, ))  
def list_attributes(request):
    disk = request.GET.get('disk',None)
    if disk is None:
        attrs = Attribute.objects.values_list('name', flat=True).distinct()
    else:
        attrs = Attribute.objects.filter(smart_report__disk=disk).values_list('name', flat=True).distinct()
    return Response(attrs)

@api_view(['GET'])
@permission_classes((ServerAuth, ))  
def disk_attribute(request):
    disk = request.GET.get('disk')
    attr = request.GET.get('attribute')
    print "%s: %s" % (attr,disk)
    attrs = Attribute.objects.filter(name=attr,smart_report__disk=disk).values('raw_value','smart_report__created')
#     attrs = Attribute.objects.filter(name=attr).values('raw_value')
    return Response(attrs)
    