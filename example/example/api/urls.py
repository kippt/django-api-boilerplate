from django.conf.urls import patterns, url

from example.api.views import *

urlpatterns = patterns('api.views',
    url(r'^account/?$', AccountView.as_view(), name='api_account'),
    
    url(r'^users/?$', UsersView.as_view(), name='api_users'),
    url(r'^users/(?P<user_id>[A-Za-z0-9_]+)/?$', UserView.as_view(), name='api_user'),
)