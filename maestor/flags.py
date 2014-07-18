from django.db.models import Max, Min
from models import Flag, DiskFlag, Disk, FlagRange, IOStat

def generate_iostat_disk_flags(disk,attr):
    for flag in Flag.objects.filter(iostat_attr=attr):
        aggregate_func = Max if flag.bad_value == 'high' else Min 
#         DiskFlag.objects.filter(flag=flag,disk=disk).delete()
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
                
def generate_disk_flag(disk,flag,value,time):
    range_match = None
    for level in FlagRange.WARNING_LEVEL_CHOICES:
        try:
            range = flag.ranges.get(level=level[0])
            if range.minimum and range.maximum:
                if value >= range.minimum and value <= range.maximum:
                    print 1
                    range_match = range
            else:
                if range.minimum and value >= range.minimum:
                        print 2
                        range_match = range
                elif range.maximum and value <= range.maximum:
                    print 3
                    range_match = range
        except:
            pass
    if range_match is not None:
        try:
            obj = DiskFlag.objects.get(disk=disk,flag=flag)
            obj.flag_range = range_match
            obj.value = value
            obj.time = time
            obj.save()
        except:
            obj = DiskFlag.objects.create(disk=disk,flag=flag,flag_range=range_match,value=value,time=time)
