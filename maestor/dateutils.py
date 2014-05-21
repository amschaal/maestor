from datetime import datetime as dt, timedelta, time
from maestor.models import Aggregate, IOStat
from django.db.models.aggregates import Max, Min, Avg, StdDev, Count
def get_week(datetime):
    date = datetime.date()
    return dt.combine(date, time()) - timedelta(days=date.weekday())
def get_next_week(datetime):
    date = datetime.date()
    return dt.combine(date, time()) + timedelta(days=7-date.weekday())
def get_hour(datetime):
    return datetime.replace(minute=0, second=0, microsecond=0)
def get_next_hour(datetime):
    return get_hour(datetime) + timedelta(hours=1)
def get_day(datetime):
    return datetime.replace(hour=0,minute=0, second=0, microsecond=0)
def get_next_day(datetime):
    return get_day(datetime) + timedelta(days=1)

def aggregate_disk(disk,beginning,unit="week"):
    if unit == "week":
        get_prev = get_week
        get_next = get_next_week
    elif unit == "hour":
        get_prev = get_hour
        get_next = get_next_hour
    elif unit == "day":
        get_prev = get_day
        get_next = get_next_day
    start = get_prev(beginning)
    end = get_next(dt.now())
    Aggregate.objects.filter(start__gte=start,time_unit=unit,disk=disk).delete()
    while start < end:
        until = get_next(start)
        for name in IOStat.objects.values_list('name', flat=True).distinct():
#             print name
            try:
                aggr = IOStat.objects.filter(created__gte=start,created__lte=until,name=name,disk=disk).values('name').annotate(max=Max('value'),min=Min('value'),average=Avg('value'),count=Count('value'),stddev=StdDev('value'))[0]
#                 print aggr
                Aggregate.objects.create(time_unit=unit,type='iostat',start=start,disk=disk,name=name,max=round(aggr['max'],2),min=round(aggr['min'],2),average=round(aggr['average'],2),stddev=round(aggr['stddev'],2),count=aggr['count'])
            except Exception, e:
#                 print e
#                 print "Couldn't aggregate for %s: %s" % (name,start)
                pass
#         for name in Attribute.objects.values_list('name', flat=True).distinct():
# #             print name
#             try:
#                 aggr = Attribute.objects.filter(smart_report__created__gte=start,smart_report__created__lte=until,name=name,smart_report__disk=disk).values('name').annotate(max=Max('value'),min=Min('value'),average=Avg('value'),count=Count('value'),stddev=StdDev('value'))[0]
# #                 print aggr
#                 Aggregate.objects.create(time_unit=unit,type='iostat',start=start,disk=disk,name=name,max=round(aggr['max'],2),min=round(aggr['min'],2),average=round(aggr['average'],2),stddev=round(aggr['stddev'],2),count=aggr['count'])
#             except Exception, e:
# #                 print e
# #                 print "Couldn't aggregate for %s: %s" % (name,start)
#                 pass
            
        start = until
        
from maestor.models import *
from maestor.dateutils import *    
# d = Disk.objects.get(id='ST3500418AS:9VMQ5KXN')
# aggregate_disk(d,dt.now())
 
for d in Disk.objects.filter(server__name__contains='bowie'):
    print d
    timestamp = dt.now()-timedelta(days=2)
    aggregate_disk(d,timestamp,unit='hour')
    aggregate_disk(d,timestamp,unit='day')
    aggregate_disk(d,timestamp,unit='week')


# class Aggregate(models.Model):
#     UNIT_CHOICES = (('hour','hour'),('day','day'),('week','week'),)
#     TYPE_CHOICES = (('smartctl','smartctl'),('iostat','iostat'),)
#     time_unit = models.CharField(max_length=10,choices=UNIT_CHOICES)
#     type = models.CharField(max_length=10,choices=TYPE_CHOICES)
#     start = models.DateTimeField()
#     disk = models.ForeignKey(Disk)
#     name = models.CharField(max_length=30)
#     number = models.IntegerField()
#     min = models.FloatField()
#     max = models.FloatField()
#     average = models.FloatField()
#     stddev = models.FloatField()
#     count = models.IntegerField()