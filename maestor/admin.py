from django.contrib import admin
from models import Disk, Server, SmartReport, Attribute
# Register your models here.

class DiskAdmin(admin.ModelAdmin):
    model = Disk
class ServerAdmin(admin.ModelAdmin):
    model = Server
class SmartReportAdmin(admin.ModelAdmin):
    model = SmartReport
class AttributeAdmin(admin.ModelAdmin):
    model = Attribute
    
admin.site.register(Disk, DiskAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(SmartReport, SmartReportAdmin)
admin.site.register(Attribute, AttributeAdmin)