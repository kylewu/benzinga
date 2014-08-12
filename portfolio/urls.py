from django.conf.urls import patterns, url


STOCK_PATTERN = r'(?P<symbol>[a-zA-Z]+)/'
QUANTITY_PATTERN = r'(?P<quantity>[0-9-]+)/'
PRICE_PATTERN = r'(?P<price>[0-9.]+)/'


urlpatterns = patterns('portfolio.views',
    url(r'^$', 'index'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
    url(r'^reset/$', 'reset'),

    url(r'^buy/' + STOCK_PATTERN + QUANTITY_PATTERN + PRICE_PATTERN + '$', 'buy'),
    url(r'^sell/' + STOCK_PATTERN + QUANTITY_PATTERN + PRICE_PATTERN + '$', 'sell'),
)
