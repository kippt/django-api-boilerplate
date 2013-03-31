import re
import json
import logging
 
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.conf import settings

logger = logging.getLogger('django.request')

class JSONResponse(HttpResponse):
    def __init__(self, request, data):
        indent = 2 if settings.DEBUG else None
        mime = "text/javascript" if settings.DEBUG else "application/json"
        content = json.dumps(data, indent=indent)
        callback = request.GET.get('callback')
        if callback:
            # verify that the callback is only letters, numbers, periods, and underscores
            if re.compile(r'^[a-zA-Z][\w.]*$').match(callback):
                content = '%s(%s);' % (callback, content)
        super(JSONResponse, self).__init__(
            content = content,
            mimetype = mime,
        )

class JSONResponseCreated(JSONResponse):
    # TODO: Add location
    def __init__(self, request, data):
        super(JSONResponse, self).__init__(request, data)

class JSONResponseNoContent(JSONResponse):
    status_code = 204

class JSONErrorResponse(JSONResponse):
    def __init__(self, request, data):
        super(JSONErrorResponse, self).__init__(request, {'message': data})

class JSONResponseBadRequest(JSONErrorResponse):
    status_code = 400

class JSONResponseUnauthorized(JSONErrorResponse):
    status_code = 401

    def __init__(self, request, data):
        super(JSONResponseUnauthorized, self).__init__(request, data)
        
        # Allow request to disable Basic Auth headers
        if not request.GET.get('disable_basic_auth'):
            self['WWW-Authenticate'] = 'Basic realm="%s"' % settings.SITE_NAME

class JSONResponseForbidden(JSONErrorResponse):
    status_code = 403

    def __init__(self, request, data='Forbidden.'):
        super(JSONResponseForbidden, self).__init__(request, data)

class JSONResponseNotFound(JSONErrorResponse):
    status_code = 404

class JSONResponseMethodNotAllowed(JSONErrorResponse):
    status_code = 405

    def __init__(self, request, data=None):
        if not data:
            data = '%s method not allowed.' % request.method
        super(JSONErrorResponse, self).__init__(request, {'error': data})

class JSONResponseNotAcceptable(JSONErrorResponse):
    status_code = 406

class JSONResponseNotImplemented(JSONErrorResponse):
    status_code = 501


class ApiView(View):
    """
    API View
    """
    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
            extra={
                'status_code': 405,
                'request': request
            }
        )
        return JSONResponseMethodNotAllowed(request)
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names and request.method.upper() in self._allowed_methods():
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
    
    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]