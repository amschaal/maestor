from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'maestor.views.index', name='index'),
    url(r'^home/$', 'maestor.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('django.contrib.auth.urls')),
    url(r'^cas/login/$', 'cas.views.login', name='cas_login'),
    url(r'^cas/logout/$', 'cas.views.logout', name='cas_logout'),
)
urlpatterns += patterns('maestor.api',
    # Examples:
    url(r'^api/smart_report/$', 'post_smart_report', name='post_smart_report'),
)
