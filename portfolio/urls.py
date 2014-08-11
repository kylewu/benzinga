from django.conf.urls import patterns, include, url


urlpatterns = patterns('portfolio.views',
    url(r'^$', 'index'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
)
