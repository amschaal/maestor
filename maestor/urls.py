from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'maestor.views.index', name='index'),
    url(r'^home/$', 'maestor.views.home', name='home'),
    url(r'^servers/$', 'maestor.views.servers', name='servers'),
    url(r'^servers/(?P<server>\d+)/disks/$', 'maestor.views.server_disks', name='server_disks'),
    url(r'^disks/(?P<disk>[:\-\w]+)/details/$', 'maestor.views.disk_details', name='disk_details'),
    url(r'^disks/by_model/$', 'maestor.views.model_disks', name='model_disks'),
    url(r'^smart_report/(?P<smart_report>[\d]+)/body/$', 'maestor.views.smart_report_body', name='smart_report_body'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('django.contrib.auth.urls')),
    url(r'^cas/login/$', 'cas.views.login', name='cas_login'),
    url(r'^cas/logout/$', 'cas.views.logout', name='cas_logout'),
)
urlpatterns += patterns('maestor.api',
    # Examples:
    url(r'^api/smart_report/$', 'post_smart_report', name='post_smart_report'),
    url(r'^api/io_report/$', 'post_io_report', name='post_io_report'),
    url(r'^api/attributes/list/$', 'list_attributes', name='list_attributes'),
    url(r'^api/disk/attribute/$', 'disk_attribute', name='disk_attribute'),
    url(r'^api/disk/values/$', 'disk_values', name='disk_values'),
    url(r'^api/io_report/count/$', 'stat_count', name='stat_count'),
)
