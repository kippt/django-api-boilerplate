import uuid
import hmac
from hashlib import sha1

from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import User

class ApiKey(models.Model):
    '''
    Api Key
    
    This key is used for API key authentication
    
    Forked from django-tastypie
    '''
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='api_key')
    key = models.CharField(max_length=256, blank=True, default='', db_index=True)
    
    created = models.DateTimeField(default=now())
    
    def __unicode__(self):
        return u"%s" % (self.user)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()

        return super(ApiKey, self).save(*args, **kwargs)

    def generate_key(self):
        new_uuid = uuid.uuid4()
        return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()