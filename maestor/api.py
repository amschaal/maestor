from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from auth import ServerAuth
from models import Server, Disk, SmartReport
from parsers import SmartParse
from django.core.exceptions import ObjectDoesNotExist
@api_view(['POST'])
@permission_classes((ServerAuth, ))  
def post_smart_report(request):
    server = request.DATA.get('server')
    body = request.DATA.get('body')
    try:
#         server = Server.objects.get(name=server)
        parser = SmartParse(body,'6.2')
        try:
            disk = Disk.objects.get(pk=parser.get_pk())
        except ObjectDoesNotExist, e:
            #disk = Disk.cre
            pass
#         Disk.objects.create()
        return Response({'body':parser.text,'info':parser.info,'attrs':parser.attrs,'pk':parser.get_pk()})
    except Exception, e:
        return Response({'status':'failed'})
    
    return Response({'status':'success'})