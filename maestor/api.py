from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONPRenderer, JSONRenderer
from auth import ServerAuth
from models import Server, Disk, SmartReport, Attribute,  IOStat, Aggregate
from parsers import SmartParse
from ioparsers import IOParse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import time
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

@api_view(['POST'])
@permission_classes((ServerAuth, ))  
def post_io_report(request):
#     print 'REQUEST........'
#     print request.DATA
#     return Response({})   
    server = request.DATA.get('server')
    data = request.DATA.get('data')
    server = Server.objects.get(name=server)
    disks = {}
   
    
    for report in data:
        for device, values in report['disks'].iteritems():
            if not disks.has_key(device):
#                 print 'Get device'
                disks[device]=Disk.objects.get(unix_device__endswith=device,server=server)
                print device
            for name, value in values.iteritems():
#                 print "%s, %s"%(name,value)
                IOStat.objects.create(disk=disks[device],server=server,created=report['timestamp'],unix_device=device,name=name,value=value)
    return Response({'server':str(server),'data':data})

#     
#     
#     parser = IOParse(body)
#     statistics = parser.parse()
#     
#     report = IOReport(server=server,text=body,parsed=datetime.now())
#     report.save()
#     
#     for device,stats in statistics.iteritems():
#         try:
#             disk = Disk.objects.get(unix_device__endswith=device,server=server)
#             for key,value in stats.iteritems():
#                 stat = IOStat(io_report=report,disk=disk,unix_device=device,name=key,value=value)
#                 stat.save()
#         except ObjectDoesNotExist, e:
#             pass
#     report.generate_read_write_rates()
#     return Response({'server':str(server),'stats':statistics})

# from maestor.models import *
# def test():
#     for r in IOReport.objects.all():
#         r.generate_read_write_rates()

@api_view(['GET'])
@permission_classes((ServerAuth, ))  
def list_attributes(request):
    disk = request.GET.get('disk',None)
    if disk is None:
        attrs = Attribute.objects.values_list('name', flat=True).distinct()
    else:
        attrs = Attribute.objects.filter(smart_report__disk=disk).values_list('name', flat=True).distinct()
    attrs = [{'type': 'smartctl', 'name': a} for a in attrs]
    iostats = [{'type': 'iostat', 'name': a} for a in IOStat.objects.values_list('name', flat=True).distinct()]
    return Response(iostats+attrs)

#@deprecated: Replaced by "disk_values" view
@api_view(['GET'])
@permission_classes((ServerAuth, ))  
def disk_attribute(request):
    disk = request.GET.get('disk')
    attr = request.GET.get('attribute')
    type = request.GET.get('type')
    print "%s: %s" % (attr,disk)
    if type == 'smartctl':
        attrs = [{'timestamp': o['smart_report__created'],'value':o['raw_value']} for o in Attribute.objects.filter(name=attr,smart_report__disk=disk).values('raw_value','smart_report__created').order_by('smart_report__created')]
    elif type == 'iostat':
        attrs = [{'timestamp': o['created'],'value':o['value']} for o in IOStat.objects.filter(name=attr,disk=disk).values('value','created').order_by('created')]
#     attrs = Attribute.objects.filter(name=attr).values('raw_value')
    return Response(attrs)
    
#@deprecated: Moving away from use of aggregate table in favor of MySQL aggregation
@api_view(['GET'])
@permission_classes((ServerAuth, ))  
@renderer_classes((JSONRenderer, JSONPRenderer))
def disk_values_old(request):
    disk = request.GET.get('disk')
    attr = request.GET.get('attribute')
    type = request.GET.get('type')
    start = request.GET.get('start',0)
    end = request.GET.get('end',0)
    
    if start == 0 or end == 0:
        if type == 'smartctl':
            start = time.mktime(Attribute.objects.filter(name=attr,smart_report__disk=disk).values_list('smart_report__created').order_by('smart_report__created')[0][0].timetuple()) *1000
            end = time.mktime(Attribute.objects.filter(name=attr,smart_report__disk=disk).values_list('smart_report__created').order_by('-smart_report__created')[0][0].timetuple()) *1000
        if type == 'iostat':
            start = time.mktime(IOStat.objects.filter(name=attr,disk=disk).values_list('created').order_by('created')[0][0].timetuple()) *1000
            end = time.mktime(IOStat.objects.filter(name=attr,disk=disk).values_list('created').order_by('-created')[0][0].timetuple()) *1000
#         start = time.mktime(Aggregate.objects.filter(type=type,disk=disk,name=attr).values_list('start').order_by('start')[0][0].timetuple()) *1000
#         end = time.mktime(Aggregate.objects.filter(type=type,disk=disk,name=attr).values_list('start').order_by('-start')[0][0].timetuple()) *1000
    range = int(end)-int(start)
    if range < 6 * 3600 * 1000:
        unit = 'default'
    elif range < 14 * 24 * 3600 * 1000:
        unit = 'hour'
    elif range < 3 * 31 * 24 * 3600 * 1000:
        unit = 'day'
    else:
        unit = 'week'

    start_dt = datetime.fromtimestamp(int(start)/1000.0)
    end_dt = datetime.fromtimestamp(int(end)/1000.0)
    print unit
    print start_dt
    print end_dt
    print "%s: %s" % (attr,disk)
    if unit == 'default':   
        if type == 'smartctl':
            fields = ['datetime','value']
            values = Attribute.objects.filter(name=attr,smart_report__disk=disk,smart_report__created__gte=start_dt,smart_report__created__lte=end_dt).values_list('smart_report__created','raw_value').order_by('smart_report__created')
        elif type == 'iostat':
            fields = ['datetime','value']
            values = IOStat.objects.filter(name=attr,disk=disk,created__gte=start_dt,created__lte=end_dt).values_list('created','value').order_by('created')
    else:
        fields = ['datetime','min','max','stddev','value','count']
        values = Aggregate.objects.filter(type=type,time_unit=unit,disk=disk,name=attr,start__gte=start_dt,start__lte=end_dt).values_list('start','min','max','stddev','average','count').order_by('start')
#     attrs = Attribute.objects.filter(name=attr).values('raw_value')
    return Response({'fields':fields,'values':values})



@api_view(['GET'])
@permission_classes((ServerAuth, ))  
@renderer_classes((JSONRenderer, JSONPRenderer))
def disk_values(request):
    from utils import fetchall
    disk = request.GET.get('disk')
    attr = request.GET.get('attribute')
    type = request.GET.get('type')
    start = request.GET.get('start',0)
    end = request.GET.get('end',0)
    
    if start == 0 or end == 0:
        if type == 'smartctl':
            start = time.mktime(Attribute.objects.filter(name=attr,smart_report__disk=disk).values_list('smart_report__created').order_by('smart_report__created')[0][0].timetuple()) *1000
            end = time.mktime(Attribute.objects.filter(name=attr,smart_report__disk=disk).values_list('smart_report__created').order_by('-smart_report__created')[0][0].timetuple()) *1000
        if type == 'iostat':
            start = time.mktime(IOStat.objects.filter(name=attr,disk=disk).values_list('created').order_by('created')[0][0].timetuple()) *1000
            end = time.mktime(IOStat.objects.filter(name=attr,disk=disk).values_list('created').order_by('-created')[0][0].timetuple()) *1000
#         start = time.mktime(Aggregate.objects.filter(type=type,disk=disk,name=attr).values_list('start').order_by('start')[0][0].timetuple()) *1000
#         end = time.mktime(Aggregate.objects.filter(type=type,disk=disk,name=attr).values_list('start').order_by('-start')[0][0].timetuple()) *1000
    range = int(end)-int(start)
    if range < 6 * 3600 * 1000:
        unit = 'default'
    elif range < 14 * 24 * 3600 * 1000:
        unit = 'hour'
    elif range < 3 * 31 * 24 * 3600 * 1000:
        unit = 'day'
    else:
        unit = 'week'

    start_dt = datetime.fromtimestamp(int(start)/1000.0)
    end_dt = datetime.fromtimestamp(int(end)/1000.0)
    
    if unit == 'default':   
        if type == 'smartctl':
            fields = ['datetime','value']
            values = Attribute.objects.filter(name=attr,smart_report__disk=disk,smart_report__created__gte=start_dt,smart_report__created__lte=end_dt).values_list('smart_report__created','raw_value').order_by('smart_report__created')
        elif type == 'iostat':
            fields = ['datetime','value']
            values = IOStat.objects.filter(name=attr,disk=disk,created__gte=start_dt,created__lte=end_dt).values_list('created','value').order_by('created')
    else:
        if unit == 'week':
            bucket = 'DATE_SUB(created, INTERVAL DAYOFWEEK(created) - 1 DAY)'
        elif unit == 'day':
            bucket = 'TIMESTAMP(DATE(created))'
        elif unit == 'hour':
            bucket = 'DATE_SUB(created, INTERVAL MINUTE(created)*60+SECOND(created) SECOND)'
        fields = ['datetime','value']
        params = (attr,disk,start_dt,end_dt)
        if type == 'smartctl':
            query =  "Select "+ bucket +" as bucket, avg(value) as AVERAGE from maestor_smartreport sr join maestor_attribute sa on sa.smart_report_id = sr.id where sa.name = %s and sr.disk_id = %s and sr.created >= %s and sr.created <= %s group by bucket;"
        elif type == 'iostat':
            query =  "Select "+ bucket +" as bucket, avg(value) as AVERAGE from maestor_iostat where name = %s and disk_id = %s and created >= %s and created <= %s group by bucket;"
        values = fetchall(query,params)
#         values = fetchall("Select DATE(DATE_SUB(created, INTERVAL DAYOFWEEK(created) - 1 DAY)) as bucket, count(*) as COUNT from maestor_smartreport sr join maestor_attribute sa on sa.smart_report_id - sr.id where sa.name = '%s' and sr.disk_id = '%s' and sr.created >= '%s' and sr.created <= '%s' group by bucket;",[attr,disk,start_dt,end_dt]);
#         print "Select DATE(DATE_SUB(created, INTERVAL DAYOFWEEK(created) - 1 DAY)) as bucket, count(*) as COUNT from maestor_smartreport sr join maestor_attribute sa on sa.smart_report_id - sr.id where sa.name = '%s' and sr.disk_id = '%s' and sr.created >= '%s' and sr.created <= '%s' group by bucket;"%[attr,disk,start_dt,end_dt]
#         values = Aggregate.objects.filter(type=type,time_unit=unit,disk=disk,name=attr,start__gte=start_dt,start__lte=end_dt).values_list('start','average').order_by('start')
#     attrs = Attribute.objects.filter(name=attr).values('raw_value')
    return Response({'fields':fields,'values':values})



@api_view(['GET'])
# @permission_classes((ServerAuth, ))  
@renderer_classes((JSONRenderer, JSONPRenderer))
def stat_count(request):
    from utils import fetchall
    disk = request.GET.get('disk', None)
#     attr = request.GET.get('attribute')
#     type = request.GET.get('type')
    start = request.GET.get('start',0)
    end = request.GET.get('end',0)
    vals = fetchall('Select DATE(DATE_SUB(created, INTERVAL DAYOFWEEK(created) - 1 DAY)) as bucket, count(*) as COUNT from maestor_smartreport group by bucket;');
    return Response(vals)
