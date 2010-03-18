from django.conf.urls.defaults import *

urlpatterns = patterns('dyndns.views',
     (r'^$' ,'update'),
     (r'^update/$' ,'update'),
)

