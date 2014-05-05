from django.db import models

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
    
class Attribute(models.Model):
    smart_report = models.ForeignKey(SmartReport)
    name = models.CharField(max_length=30)
    value = models.IntegerField()
    worst = models.IntegerField()
    thresh = models.IntegerField()
    failed = models.DateTimeField(null=True,blank=True)
    raw_value = models.CharField(max_length=25)
    def __unicode__(self):
        return '%s: %s'%(self.smart_report.disk, self.name)
    
