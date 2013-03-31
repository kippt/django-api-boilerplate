from django.conf.urls import patterns, url

from example.api.views import *

urlpatterns = patterns('api.views',
    # Simple helper function to echo data back
    url(r'^echo/?$', EchoView.as_view(), name='api_echo'),
    
    # User account - Returns API key
    url(r'^account/?$', AccountView.as_view(), name='api_account'),
    
    # Sample API
    url(r'^users/?$', UsersView.as_view(), name='api_users'),
    url(r'^users/(?P<user_id>[A-Za-z0-9_]+)/?$', UserView.as_view(), name='api_user'),
)