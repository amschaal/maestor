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
    
    server = Server.objects.get(name=server)
    parser = SmartParse(body,'6.2')
    
    try:
        server = Server.objects.get(name=server)
        parser = SmartParse(body,'6.2')
        
        try:
            disk = Disk.objects.get(pk=parser.get_pk())
        except ObjectDoesNotExist, e:
            disk = Disk(pk=parser.get_pk(),server=server,**parser.info)
            disk.save()
        SM = SmartReport(disk=disk,server=server,firmware=parser.info['firmware'],text=body,parsed=datetime.now(),ip=request.META['REMOTE_ADDR'])
        SM.save()
        '''
    smart_report = models.ForeignKey(SmartReport)
    name = models.CharField(max_length=30)
    value = models.IntegerField()
    worst = models.IntegerField()
    thresh = models.IntegerField()
    failed = models.DateTimeField(null=True,blank=True)
    raw_value = models.CharField(max_length=25)
        "raw_value": "3707945", 
            "updated": "Always", 
            "name": "Raw_Read_Error_Rate", 
            "value": "102", 
            "failed": "-", 
            "thresh": "006", 
            "worst": "099", 
            "type": "Pre-fail", 
            "id": "1"
        '''
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
    return Response(Attribute.objects.values_list('name').distinct())
    