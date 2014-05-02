from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'login.views.index', name='index'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('django.contrib.auth.urls')),
    url(r'^cas/login/$', 'cas.views.login', name='cas_login'),
    url(r'^cas/logout/$', 'cas.views.logout', name='cas_logout'),
)
