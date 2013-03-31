from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from annoying.functions import get_object_or_None

from api_boilerplate.http import ApiView, JSONResponse, JSONResponseNotFound
from api_boilerplate.pagination import Paginator
from api_boilerplate.decorators import api_login_required
from api_boilerplate.exceptions import ApiBadRequestException

from example.api.models import UserProfile


def _get_user(request, user_id):
    '''
    Helper function for parsing user
    '''
    user = None
    # /api/users/self/
    if request.user.is_authenticated() and (user_id == 'self'):
        user = request.user
    # /api/users/1/
    elif user_id.isdigit():
        user = get_object_or_None(User, is_active=True, pk=user_id)
    # /api/users/jorilallo/
    else:
        user = get_object_or_None(User, is_active=True, username__iexact=user_id)
    return user


class AccountView(ApiView):
    '''
    Account view
    
    Endpoint:
        /api/account/
    
    Attributes:
        None
    Parameters:
        None
    
    Visibility
        Private - requires auth
    '''
    
    @method_decorator(api_login_required)
    def get(self, request, *args, **kwargs):
        return JSONResponse(request, request.user.profile.api(include_account=True))


class UsersView(ApiView):
    '''
    Users view
    
    Endpoint:
        /api/users/
    
    Attributes:
        None
    Parameters:
        None
    
    Visibility
        Public
    '''
    
    def get(self, request, *args, **kwargs):
        profiles = UserProfile.objects.all()
        
        paginator = Paginator(request.GET, profiles, resource_uri='/api/users/')
        try:
            paginator_page = paginator.page()
            paginator_objects = paginator_page['objects']
            paginator_meta = paginator_page['meta']
        except ApiBadRequestException as e:
            return JSONResponseBadRequest(request, e.message)
        
        objects = []
        for profile in paginator_objects:
            objects.append(profile.api())
        
        data = {
            'meta': paginator_meta,
            'objects': objects,
        }
        return JSONResponse(request, data)


class UserView(ApiView):
    '''
    User view
    
    Endpoint:
        /api/users/<user_id>/
    
    Attributes:
        None
    Parameters:
        None
    
    Visibility
        Public
    '''
    
    def get(self, request, user_id, *args, **kwargs):
        ## Determine user
        user = _get_user(request,user_id)
        
        if user:
            return JSONResponse(request, user.get_profile().api())
        return JSONResponseNotFound(request, 'User not found.')
        