from django.db import models

class Disk(models.Model):
    pk = models.CharField(max_length=30, primary_key=True)
    serial = models.CharField(max_length=15)
    model = models.CharField(max_length=20)
    family = models.CharField(max_length=50,blank=True,null=True)
    rpm = models.IntegerField()
    capacity = models.CharField(max_length=8,blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    #...more fields coming...#
    
class Report(models.Model):
    disk = models.ForeignKey(Disk)
    server = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    smart_version = models.CharField(max_length=3)
    text = models.TextField()
    parsed = models.DateTimeField(blank=True,null=True)
    
class Attribute(models.Model):
    report = models.ForeignKey(Report)
    name = models.CharField(max_length=30)
    value = models.IntegerField()
    worst = models.IntegerField()
    thresh = models.IntegerField()
    
    
