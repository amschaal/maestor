from django.db.models import Max, Min
from models import Flag, DiskFlag, Disk, FlagRange, IOStat
                
def generate_disk_flag(disk,flag,value,time):
    range_match = None
    for level in FlagRange.WARNING_LEVEL_CHOICES:
        try:
            range = flag.ranges.get(level=level[0])
            if range.minimum and range.maximum:
                if value >= range.minimum and value <= range.maximum:
                    range_match = range
            else:
                if range.minimum and value >= range.minimum:
                        range_match = range
                elif range.maximum and value <= range.maximum:
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

#NOT USED: Generate DiskFlags based on the all time min/max from IOStat (need to add more logic for smartctl)
#Leaving here for code reference
def generate_flags(flags):
    from django.db.models import Max, Min
    for flag in flags:
        aggregate_func = Max if flag.bad_value == 'high' else Min 
        DiskFlag.objects.filter(flag=flag).delete()
        if flag.iostat_attr:
            
            #For each level from minor to severe, see if any disks match the criteria
            for level in FlagRange.WARNING_LEVEL_CHOICES:
                query= {'name':flag.iostat_attr}
                try:
                    range = flag.ranges.get(level=level[0])
                    if range.minimum:
                        query['value__gte'] = range.minimum
                    if range.maximum:
                        query['value__lte'] = range.maximum
                    for result in IOStat.objects.filter(**query).values('disk').annotate(value=(aggregate_func('value'))):
                        try:
                            obj = DiskFlag.objects.get(disk_id=result['disk'],flag=flag)
                            obj.value = result.value
                            obj.save()
                        except:
                            obj = DiskFlag.objects.create(disk_id=result['disk'],flag=flag,flag_range=range,value=result['value'])
                        
                except Exception, e:
                    print  level[0]
                    print e
                        
