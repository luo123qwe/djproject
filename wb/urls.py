
from django.conf.urls.defaults import *

urlpatterns = patterns('wb.views',
    (r'^$', 'login'),
    (r'^login_check/$', 'login_check'),
    (r'logout/$', 'logout'),
)

