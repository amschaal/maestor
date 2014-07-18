from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save

import re

class Server(models.Model):
    name = models.CharField(max_length=50)
    ip = models.IPAddressField()
    api_key = models.CharField(max_length=30)
    def __unicode__(self):
        return self.name

class Disk(models.Model):
    id = models.CharField(max_length=60,primary_key=True)
    server = models.ForeignKey(Server,related_name='disks')
    slot = models.CharField(max_length=100,blank=True,null=True)
    unix_device = models.CharField(max_length=100,blank=True,null=True)
    serial = models.CharField(max_length=30)
    model = models.CharField(max_length=30)
    firmware = models.CharField(max_length=20)
    family = models.CharField(max_length=50,blank=True,null=True)
    rpm = models.IntegerField(blank=True,null=True)
    gigabytes = models.IntegerField(blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return '%s: %s'%(self.server,self.pk)

# class IOReport(models.Model):
#     server = models.ForeignKey(Server)
#     created = models.DateTimeField(auto_now_add=True)
#     text = models.TextField()
#     parsed = models.DateTimeField(blank=True,null=True)
#     def __unicode__(self):
#         return '%s: %s'%(self.server, self.created)
#     def get_previous_report(self):
#         return IOReport.objects.filter(created__lt=self.created, server=self.server).order_by('-created')[0]
#     def generate_read_write_rates(self):
#         try:
#             last = self.get_previous_report()
#             if not last:
#                 return
#             devices =  [d['unix_device'] for d in IOStat.objects.filter(io_report=self).values('unix_device').distinct()]
#             for device in devices:
#                 kB_read = IOStat.objects.get(io_report=self,name='kB_read',unix_device=device)
#                 kB_wrtn = IOStat.objects.get(io_report=self,name='kB_wrtn',unix_device=device)
#                 kB_read_last = IOStat.objects.get(io_report=last,name='kB_read',unix_device=device)
#                 kB_wrtn_last = IOStat.objects.get(io_report=last,name='kB_wrtn',unix_device=device)
#                 obj, created = IOStat.objects.get_or_create(io_report=self,disk=kB_read.disk,unix_device=kB_read.unix_device,name='read_rate')
#                 if created:
#                     print 'read created'
#                     obj.value = str(round((float(kB_read.value)-float(kB_read_last.value))/(kB_read.io_report.created-kB_read_last.io_report.created).total_seconds(),3))
#                     print obj.value
#                     obj.save()
#                 obj, created = IOStat.objects.get_or_create(io_report=self,disk=kB_read.disk,unix_device=kB_read.unix_device,name='write_rate')
#                 if created:
#                     print 'write created'
#                     obj.value = str(round((float(kB_wrtn.value)-float(kB_wrtn_last.value))/(kB_wrtn.io_report.created-kB_wrtn_last.io_report.created).total_seconds(),3))
#                     print obj.value
#                     obj.save()    
#         except Exception, e:
#             print e
    
class IOStat(models.Model):
#     io_report = models.ForeignKey(IOReport)
    disk = models.ForeignKey(Disk,related_name='io_reports')
    server = models.ForeignKey(Server)
    created = models.DateTimeField()
    unix_device = models.CharField(max_length=100)
    name = models.CharField(max_length=30)
    value = models.FloatField()#models.CharField(max_length=25)
    def __unicode__(self):
        return '%s: %s'%(self.disk, self.name)
@receiver(post_save, sender=IOStat)
def IOStat_post_save(sender, instance, **kwargs):
    from maestor.flags import generate_disk_flag
    try:
        flag = Flag.objects.get(iostat_attr=instance.name)
        generate_disk_flag(instance.disk,flag,instance.value,instance.created)
    except:
        pass


class SmartReport(models.Model):
    disk = models.ForeignKey(Disk,related_name='smart_reports')
    server = models.ForeignKey(Server)
    ip = models.IPAddressField()
    slot = models.CharField(max_length=100)
    unix_device = models.CharField(max_length=100)
    firmware = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    smart_version = models.CharField(max_length=3)
    text = models.TextField()
    parsed = models.DateTimeField(blank=True,null=True)
    def __unicode__(self):
        return '%s: %s'%(self.disk, self.created)
    def get_previous_report(self):
        return SmartReport.objects.filter(created__lt=self.created, disk=self.disk).order_by('-created')[0]
    
class Attribute(models.Model):
    smart_report = models.ForeignKey(SmartReport)
    name = models.CharField(max_length=30)
    value = models.IntegerField()
    worst = models.IntegerField()
    thresh = models.IntegerField()
    failed = models.DateTimeField(null=True,blank=True)
    raw_value = models.IntegerField()
#     def parse_raw_value(self):
#         try:
#             return float(re.search(r'(\d+\.?\d*)',self.raw_value).group(1))
#         except:
#             return None
    def __unicode__(self):
        return '%s: %s'%(self.smart_report.disk, self.name)
    
    
class Aggregate(models.Model):
    UNIT_CHOICES = (('hour','hour'),('day','day'),('week','week'),)
    TYPE_CHOICES = (('smartctl','smartctl'),('iostat','iostat'),)
    time_unit = models.CharField(max_length=10,choices=UNIT_CHOICES)
    type = models.CharField(max_length=10,choices=TYPE_CHOICES)
    start = models.DateTimeField()
    disk = models.ForeignKey(Disk)
    name = models.CharField(max_length=30)
    min = models.FloatField()
    max = models.FloatField()
    average = models.FloatField()
    stddev = models.FloatField()
    count = models.IntegerField()
    
class WarningCriteria(models.Model):
    WARNING_LEVEL_CHOICES = (('minor','Minor'),('moderate','Moderate'),('severe','Severe'),)
    BAD_VALUE_CHOICES = (('high','High values are bad'),('low','Low values are bad'),)
    level = models.CharField(max_length=10,choices=WARNING_LEVEL_CHOICES)
    iostat_attr = models.CharField(max_length=30,blank=True,null=True)
    smartreport_attr = models.CharField(max_length=30,blank=True,null=True)
    minimum = models.DecimalField(max_digits=16,decimal_places=3,blank=True,null=True)
    maximum = models.DecimalField(max_digits=16,decimal_places=3,blank=True,null=True)
    bad_value = models.CharField(max_length=10,choices=BAD_VALUE_CHOICES)
    def __unicode__(self):
        if self.iostat_attr:
            return '%s: IOStat %s (%s-%s)'%(self.level.capitalize(), self.iostat_attr,self.minimum,self.maximum)
        elif self.smartreport_attr:
            return '%s: SmartReport %s (%s-%s)'%(self.level.capitalize(), self.smartreport_attr,self.minimum,self.maximum)

class Flag(models.Model):
    BAD_VALUE_CHOICES = (('high','High values are bad'),('low','Low values are bad'),)
    iostat_attr = models.CharField(max_length=30,blank=True,null=True)
    smartreport_attr = models.CharField(max_length=30,blank=True,null=True)
    bad_value = models.CharField(max_length=10,choices=BAD_VALUE_CHOICES)
    
    def __unicode__(self):
        if self.iostat_attr:
            return 'IOStat %s'%(self.iostat_attr)
        elif self.smartreport_attr:
            return 'SmartReport %s'%(self.smartreport_attr)



        
class FlagRange(models.Model):
    WARNING_LEVEL_CHOICES = (('minor','Minor'),('moderate','Moderate'),('severe','Severe'),)
    flag = models.ForeignKey(Flag,related_name="ranges")
    level = models.CharField(max_length=10,choices=WARNING_LEVEL_CHOICES)
    minimum = models.DecimalField(max_digits=16,decimal_places=3,blank=True,null=True)
    maximum = models.DecimalField(max_digits=16,decimal_places=3,blank=True,null=True)
    
class DiskFlag(models.Model):
    flag = models.ForeignKey(Flag,related_name="disk_flags")
    flag_range = models.ForeignKey(FlagRange,related_name="disk_flags")
    disk = models.ForeignKey(Disk,related_name="disk_flags")
    updated = models.DateTimeField(auto_now_add=True)
    time = models.DateTimeField(blank=True,null=True)
    value = models.DecimalField(max_digits=16,decimal_places=3)
