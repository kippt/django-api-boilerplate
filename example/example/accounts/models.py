from django.db import models
from django.contrib.auth.models import User

from calendar import timegm as epoch

from api_boilerplate.models import ApiKey

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    
    
    def __unicode__(self):
        return u'%s' % (self.user.username)
    
    def get_api_key(self):
        api_key, created = ApiKey.objects.get_or_create(user=self.user)
        return api_key.key
    
    def api(self, include_account=False):
        user = self.user
        data = {
            'username': user.username,
            'is_admin': user.is_staff,
            'joined_at': epoch(user.date_joined.timetuple()),
            'resource_uri': '/api/users/%s/' % user.pk,
        }
        
        # Return API key when account info is requested
        if include_account:
            data['api_key'] = self.get_api_key()
        
        return data

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])