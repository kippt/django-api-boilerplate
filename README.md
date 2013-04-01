# django-api-boilerplate

This project is meant to provide the basics for people to create well behaving APIs for Django projects. It's not an app for automatically creating APIs like tastypie or piston. Instead it provides the building blocks which you can use to roll out your own RESTful API fast with Django's Class based views. This provides:

- Class based API views and decorators
- API Responses for different HTTP codes
- Model pagination
- Authentication middlewares:
    - Django cookies
    - HTTP Basic
    - API Key

Most of this code is extracted from [Kippt's](kippt.com/) API ([documentation on Github](https://github.com/kippt/api-documentation/)). It's designed to be as easy as possible to consume, mainly meaning simple authentication (browser session) and JSON output. This makes API debugging extremely easy with Chrome's JSONView and Postman extensions. You should also be using [requests](https://github.com/kennethreitz/requests).

Some of the code in this project is influenced by or forked from awesome [django-tastypie](https://github.com/toastdriven/django-tastypie). HTTP responses are created based on work of [Leah Culver](https://github.com/leah) and [Eric Florenzano](https://github.com/ericflo).

## Settings

### API_KEY_MODEL

_Default: api_boilerplate.models.ApiKey_

### API_LIMIT_PER_PAGE

_Default: 20_

### API_AUTH_CASE_INSENSITIVE

_Default: False_

### API_AUTH_EMAIL_AS_USERNAME

_Default: False_

### API_REQUEST_JSON

_Default: True_

## Common best practices

- Use _api()_ method for resource Models to return a Python object. Responses will convert that into JSON. This will make caching easier as well.

## Todo

- Docs all the things
- Better name
- Test all the things
- Separation for /api/ url (usually the redirect for docs)
- JSONP and errors
    - Better way of handling error messages
    - Have a separate field for error messages in JSONP response
- Rate limiting (Cache/Redis based)
