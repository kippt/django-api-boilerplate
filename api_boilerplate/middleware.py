import base64
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.loading import get_model
from annoying.functions import get_object_or_None

from api_boilerplate.http import JSONResponseUnauthorized, JSONResponseBadRequest

API_KEY_MODEL = getattr(settings, 'API_KEY_MODEL',
    'api_boilerplate.models.ApiKey')
ApiKey = get_model(*API_KEY_MODEL.split('.',1))

class ApiDjangoAuthMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Django session auth
        
        Authenticates logged in users. Handy for quick debugging or extensions.
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

            try:
                # Get user by username or email
                user = get_object_or_None(User, username__iexact=bits[0])
                if not user:
                    user = get_object_or_None(User, email__iexact=bits[0])
                
                if user.check_password(bits[1]):
                    request.user = user
                else:
                    return JSONResponseUnauthorized(request, 'Username and password don\'t match')
            except:
                return JSONResponseUnauthorized(request, 'Username and password don\'t match')
            
            request.user = user
            return

class ApiKeyAuthMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Middleware for API authentication. Partly forked form django-tastypie
        """
        # ApiKey Auth
        username = request.META.get('HTTP_X_KIPPT_USERNAME', None)
        api_key = request.META.get('HTTP_X_KIPPT_API_TOKEN', None)

        if username and api_key:
            '''
            Handles API key auth, in which a user provides a username & API key.
            '''
            try:
                # Get user by username or email
                user = get_object_or_None(User, username__iexact=username)
                if not user:
                    user = get_object_or_None(User, email__iexact=username)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                return JSONResponseUnauthorized(request, 'Can\'t find an user with this username and api_key')

            try:
                ApiKey.objects.get(user=user, key=api_key)
            except ApiKey.DoesNotExist:
                return JSONResponseUnauthorized(request, 'Can\'t find an user with this username and api_key')

            request.user = user
            return
