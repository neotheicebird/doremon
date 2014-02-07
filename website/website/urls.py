from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from timeline.views import home, tags, filter_tags

urlpatterns = patterns('',
    # Examples:
    # url(r'^$',i 'website.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home),
    url(r'^tags/$', tags),
    url(r'^tags/([^/]+)/$', filter_tags),
)
