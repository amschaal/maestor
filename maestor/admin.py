from django.contrib import admin
from django import forms
from models import Disk, Server, SmartReport, Attribute, WarningCriteria, IOStat, Flag, FlagRange
# Register your models here.

class DiskAdmin(admin.ModelAdmin):
    model = Disk
class ServerAdmin(admin.ModelAdmin):
    model = Server
class SmartReportAdmin(admin.ModelAdmin):
    model = SmartReport
class AttributeAdmin(admin.ModelAdmin):
    model = Attribute


class CriteriaForm(forms.ModelForm):
    smartreport_attr = forms.ChoiceField(required=False,choices=[('','---------')]+[(attr,attr) for attr in Attribute.objects.all().order_by('name').values_list('name', flat=True).distinct()])
    iostat_attr = forms.ChoiceField(required=False,choices=[('','---------')]+[(attr,attr) for attr in IOStat.objects.all().order_by('name').values_list('name', flat=True).distinct()])
#     def __init__(self, *args, **kwargs):
#         super(MyForm, self).__init__(*args, **kwargs)
#         self.fields['afield'].choices = my_computed_choices
    def clean(self):
        cleaned_data = super(CriteriaForm, self).clean()  # Get the cleaned data from default clean, returns cleaned_data
        smartreport_attr = cleaned_data.get("smartreport_attr")
        iostat_attr = cleaned_data.get("iostat_attr")
        minimum = cleaned_data.get("minimum")
        maximum = cleaned_data.get("maximum")
        if minimum is None and maximum is None:
            self._errors['minimum']= self.error_class(['Please choose at least a minimum or a maximum value.'])
            self._errors['maximum']= self.error_class(['Please choose at least a minimum or a maximum value.'])
        if iostat_attr == '' and smartreport_attr == '' or iostat_attr and smartreport_attr:
            self._errors['iostat_attr']= self.error_class(['Please choose EITHER a Smart Report attribute OR an IOStat attribute.'])
            self._errors['smartreport_attr']= self.error_class(['Please choose EITHER a Smart Report attribute OR an IOStat attribute.'])
        
        return cleaned_data
    class Meta:
        model = WarningCriteria
#         exclude = ['name']
def Criteria(obj):
    color = {'minor':'yellow','moderate':'orange','severe':'red'}[obj.level]
    return '<span style="background-color:%s;">%s</span>' % (color,obj)
Criteria.short_description = 'Warning criteria'
Criteria.allow_tags = True
class CriteriaAdmin(admin.ModelAdmin):
#     exclude = ['age']
    form = CriteriaForm
    list_display = (Criteria,)
    
class FlagRangeForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(FlagRangeForm, self).clean()  # Get the cleaned data from default clean, returns cleaned_data
        minimum = cleaned_data.get("minimum")
        maximum = cleaned_data.get("maximum")
        if minimum is None and maximum is None:
            self._errors['minimum']= self.error_class(['Please choose at least a minimum or a maximum value.'])
            self._errors['maximum']= self.error_class(['Please choose at least a minimum or a maximum value.'])
        return cleaned_data
    class Meta:
        model = FlagRange
class FlagRangeInline(admin.TabularInline):
    model = FlagRange
    form = FlagRangeForm

class FlagForm(forms.ModelForm):
    smartreport_attr = forms.ChoiceField(required=False,choices=[('','---------')]+[(attr,attr) for attr in Attribute.objects.all().order_by('name').values_list('name', flat=True).distinct()])
    iostat_attr = forms.ChoiceField(required=False,choices=[('','---------')]+[(attr,attr) for attr in IOStat.objects.all().order_by('name').values_list('name', flat=True).distinct()])
    def clean(self):
        cleaned_data = super(FlagForm, self).clean()  # Get the cleaned data from default clean, returns cleaned_data
        smartreport_attr = cleaned_data.get("smartreport_attr")
        iostat_attr = cleaned_data.get("iostat_attr")
        if iostat_attr == '' and smartreport_attr == '' or iostat_attr and smartreport_attr:
            self._errors['iostat_attr']= self.error_class(['Please choose EITHER a Smart Report attribute OR an IOStat attribute.'])
            self._errors['smartreport_attr']= self.error_class(['Please choose EITHER a Smart Report attribute OR an IOStat attribute.'])
        return cleaned_data
    class Meta:
        model = Flag

class FlagAdmin(admin.ModelAdmin):
    form = FlagForm
    inlines = [FlagRangeInline,]
#     list_display = (Criteria,)


# class Flag(models.Model):
#     BAD_VALUE_CHOICES = (('high','High values are bad'),('low','Low values are bad'),)
#     iostat_attr = models.CharField(max_length=30,blank=True,null=True)
#     smartreport_attr = models.CharField(max_length=30,blank=True,null=True)
#     bad_value = models.CharField(max_length=10,choices=BAD_VALUE_CHOICES)
#     
#     def __unicode__(self):
#         if self.iostat_attr:
#             return '%s: IOStat %s'%(self.level.capitalize(), self.iostat_attr)
#         elif self.smartreport_attr:
#             return '%s: SmartReport %s'%(self.level.capitalize(), self.smartreport_attr)
# 
#         
# class FlagRange(models.Model):
#     WARNING_LEVEL_CHOICES = (('minor','Minor'),('moderate','Moderate'),('severe','Severe'),)
#     flag = models.ForeignKey(Flag,related_name="ranges")
#     level = models.CharField(max_length=10,choices=WARNING_LEVEL_CHOICES)
#     minimum = models.DecimalField(max_digits=16,decimal_places=3,blank=True,null=True)
#     maximum = models.DecimalField(max_digits=16,decimal_places=3,blank=True,null=True)
    
admin.site.register(Disk, DiskAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(SmartReport, SmartReportAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(WarningCriteria, CriteriaAdmin)
admin.site.register(Flag, FlagAdmin)