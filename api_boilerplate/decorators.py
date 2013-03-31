from django.contrib.auth.models import User

from api_boilerplate.http import JSONResponseUnauthorized, JSONResponseNotAcceptable, JSONResponseBadRequest

def api_login_required(function):
    """
    Decorator to check that user is logged in.
    """
    def _dec(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Django Auth
            if request.user.is_authenticated():
                return view_func(request, *args, **kwargs)
            else:
                # No authentication provided
                return JSONResponseUnauthorized(request, 'Please authenticate')
        return _wrapped_view
    if function:
        return _dec(function)
    return _dec


def staff_required(function):
    """
    Decorator to check for user's staff status.
    
    Requires user to be logged in (*doh*)
    """
    def _dec(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Django Auth
            user = request.user
            if user.is_authenticated() and (user.is_staff or user.is_superuser):
                return view_func(request, *args, **kwargs)
            else:
                # No authentication provided
                return JSONResponseUnauthorized(request, 'Please authenticate')
        return _wrapped_view
    if function:
        return _dec(function)
    return _dec
