from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save

import re, datetime

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
        generate_disk_flag(instance.disk,flag,instance.value,datetime.datetime.now())
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
@receiver(post_save, sender=Attribute)
def Attribute_post_save(sender, instance, **kwargs):
    from maestor.flags import generate_disk_flag
    try:
        flag = Flag.objects.get(smartreport_attr=instance.name)
        generate_disk_flag(instance.smart_report.disk,flag,instance.value,datetime.datetime.now())
    except:
        pass
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
    def attr_name(self):
        return self.iostat_attr if self.iostat_attr else self.smartreport_attr
    def attr_type(self):
        return 'iostat' if self.iostat_attr else 'smartctl'
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
    @staticmethod
    def choice_value(choice):
        return [choice[0] for choice in FlagRange.WARNING_LEVEL_CHOICES].index(choice)
            
class DiskFlag(models.Model):
    flag = models.ForeignKey(Flag,related_name="disk_flags")
    flag_range = models.ForeignKey(FlagRange,related_name="disk_flags")
    disk = models.ForeignKey(Disk,related_name="disk_flags")
    updated = models.DateTimeField(auto_now_add=True)
    time = models.DateTimeField(blank=True,null=True)
    value = models.DecimalField(max_digits=16,decimal_places=3)
    worst_time = models.DateTimeField(blank=True,null=True)
    worst_value = models.DecimalField(max_digits=16,decimal_places=3,blank=True,null=True)