import base64
import json

from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.loading import get_model

from api_boilerplate.http import JSONResponseUnauthorized, JSONResponseBadRequest

### Settings

AUTH_CASE_INSENSITIVE = getattr(settings, 'API_AUTH_CASE_INSENSITIVE', False)

AUTH_EMAIL_AS_USERNAME = getattr(settings, 'API_AUTH_EMAIL_AS_USERNAME', False)

API_KEY_MODEL = getattr(settings, 'API_KEY_MODEL',
    'api_boilerplate.models.ApiKey')
ApiKey = get_model(*API_KEY_MODEL.split('.',1))

REQUEST_JSON = getattr(settings, 'API_REQUEST_JSON', True)

### Helper functions

def _get_user(username):
    try:
        if AUTH_CASE_INSENSITIVE:
            user = User.objects.get(username__iexact=username)
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    
    if AUTH_EMAIL_AS_USERNAME:
        if not user:
            try:
                if AUTH_CASE_INSENSITIVE:
                    user = User.objects.get(email__iexact=username)
                else:
                    user = User.objects.get(email=username)
            except User.DoesNotExist:
                user = None
    
    return user

### Authentication middlewares

class ApiDjangoAuthMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Django session auth
        
        Authenticates logged in users. Handy for quick debugging or extensions.
        
        Note: Only allows CSRF safe methods. See Django's CSRF AJAX documentation for including tokens to requests:
        
            https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
        
        """
        if request.user.is_authenticated():
            return None

class ApiHttpBasicAuthMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Middleware for API authentication.
        
        Partly forked from django-tastypie
        """
        # Basic Auth
        if request.META.get('HTTP_AUTHORIZATION', None):
            try:
                (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()
                if auth_type != 'Basic':
                    return JSONResponseUnauthorized(request, 'Error with HTTP Basic Auth')
                user_pass = base64.b64decode(data)
            except:
                return JSONResponseUnauthorized(request, 'Error with HTTP Basic Auth')

            bits = user_pass.split(':', 1)

            if len(bits) != 2:
                return JSONResponseUnauthorized(request, 'Invalid Authorization header. Value should be "Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==" where base64 encoded part is encrypted from "username:password"')

            
            # Get user by username or email
            username = bits[0]
            user = _get_user(username)
            if user == None:
                return JSONResponseUnauthorized(request, 'User and password don\'t match')
            
            if user.check_password(bits[1]):
                request.user = user
            else:
                return JSONResponseUnauthorized(request, 'Username and password don\'t match')
            
            request.user = user
            return

class ApiKeyAuthMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Middleware for API authentication. Partly forked form django-tastypie
        """
        # ApiKey Auth
        username = request.META.get('HTTP_X_%s_USERNAME' % (settings.SITE_NAME.upper()), None) 
        api_key = request.META.get('HTTP_X_%s_API_TOKEN' % (settings.SITE_NAME.upper()), None)

        if username and api_key:
            '''
            Handles API key auth, in which a user provides a username & API key.
            '''
            user = _get_user(username)
            if user == None:
                return JSONResponseUnauthorized(request, 'Can\'t find an user with this username and api_key')

            try:
                ApiKey.objects.get(user=user, key=api_key)
            except ApiKey.DoesNotExist:
                return JSONResponseUnauthorized(request, 'Can\'t find an user with this username and api_key')

            request.user = user
            return

### Request middlewares

class ApiRequestDataMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Middleware for parsing POST/PUT/PATCH data.
        
        Parses POST data into request.data. Optionally parses JSON from raw content as well (default=True).
        """
        
        # JSON
        if REQUEST_JSON:
            try:
                data = json.loads(request.body)
            except ValueError:
                data = None
        
        # POST
        if request.method == 'POST' and request.POST.keys():
            data = {}
            for key in request.POST.keys():
                data[key] = request.POST[key]
        
        request.data = data
        return
