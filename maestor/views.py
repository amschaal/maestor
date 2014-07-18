from django.shortcuts import render, redirect
from maestor.models import Disk, Server, SmartReport, Attribute, WarningCriteria, IOStat, Flag, DiskFlag, FlagRange
import datetime
def index(request):
    if request.user.is_authenticated():
        return redirect('home')
    context = {}
    return render(request, 'maestor/index.html', context)

def home_old(request):
    warnings = []
    for criteria in WarningCriteria.objects.all():
        query = {}
        if criteria.minimum:
            query['value__gte'] = criteria.minimum
        if criteria.maximum:
            query['value__lte'] = criteria.maximum
        if criteria.iostat_attr:
            query['name']=criteria.iostat_attr
            results = IOStat.objects.filter(**query).values_list('created','name','value')
            warnings += [[criteria] + list(result) for result in results]
#             print results
        if criteria.smartreport_attr:
            query['name']=criteria.smartreport_attr
            results = Attribute.objects.filter(**query).values_list('smart_report__created','name','value')#extra(select={'created':'smart_attribute__created'}).
            warnings += [[criteria] + list(result) for result in results]
#             print results
    print warnings
    context = {'warnings':warnings}
    return render(request, 'maestor/home.html', context)

def generate_warnings(flags):
    from django.db.models import Max, Min
    for flag in flags:
        aggregate_func = Max if flag.bad_value == 'high' else Min 
        DiskFlag.objects.filter(flag=flag).delete()
        if flag.iostat_attr:
            
            #For each level from minor to severe, see if any disks match the criteria
            for level in FlagRange.WARNING_LEVEL_CHOICES:
                query= {'name':flag.iostat_attr}
#                 for result in IOStat.objects.filter(query).values('disk').annotate(value=(aggregate_func('value'))):
                try:
                    range = flag.ranges.get(level=level[0])
                    if range.minimum:
                        query['value__gte'] = range.minimum
                    if range.maximum:
                        query['value__lte'] = range.maximum
                    for result in IOStat.objects.filter(**query).values('disk').annotate(value=(aggregate_func('value'))):
#                         print flag
#                         print result['disk']
                        try:
                            obj = DiskFlag.objects.get(disk_id=result['disk'],flag=flag)
                            obj.value = result.value
                            obj.save()
                        except:
                            obj = DiskFlag.objects.create(disk_id=result['disk'],flag=flag,flag_range=range,value=result['value'])
#                         obj.flag_range = range
# #                         obj.time = datetime.datetime.now()
                        
                except Exception, e:
                    print  level[0]
                    print e
                        
#                     for disk in IOStat.objects.filter(name=flag.iostat_attr, )
                    
            
#             disks = IOStat.objects.filter(name=flag.iostat_attr).values('disk_id').distinct()
#             for disk in disks:
#                 query['disk'] = disk['disk_id']
#                 try:
#                     warnings.append( {'criteria':criteria,'disk':IOStat.objects.filter(**query).order_by('-created')[0]})
#                 except:
#                     pass


def home(request):
    context={'flags':DiskFlag.objects.all()}
    return render(request, 'maestor/home.html', context)
    warnings = []
    for criteria in WarningCriteria.objects.all():
        query = {}
        if criteria.minimum:
            query['value__gte'] = criteria.minimum
        if criteria.maximum:
            query['value__lte'] = criteria.maximum
        if criteria.iostat_attr:
            query['name'] = criteria.iostat_attr
            disks = IOStat.objects.filter(name=criteria.iostat_attr).values('disk_id','name').distinct()
#             print disks
            for disk in disks:
                query['disk'] = disk['disk_id']
#                 print query
                try:
                    warnings.append( {'criteria':criteria,'disk':IOStat.objects.filter(**query).order_by('-created')[0]})
                except:
#                     print 'OOpsss!!!'
                    pass
        if criteria.smartreport_attr:
            query['name'] = criteria.smartreport_attr
            disks = Attribute.objects.filter(name=criteria.smartreport_attr).values('smart_report__disk_id','name').distinct()
#             print disks
            for disk in disks:
                query['smart_report__disk'] = disk['smart_report__disk_id']
#                 print query
                try:
                    warnings.append( {'criteria':criteria,'disk':Attribute.objects.filter(**query).order_by('-smart_report__created')[0]})
                except:
#                     print 'OOpsss!!!'
                    pass
    context = {'warnings':warnings}
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
