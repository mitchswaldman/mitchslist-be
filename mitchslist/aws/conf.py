import datetime, os
# Helper function for getting environment variables (defaults to exception)
from django.core.exceptions import ImproperlyConfigured
def get_env_variable(var_name, env_name=None):
    try:
        return eval(var_name)
    except NameError:
        try:
            return os.environ[env_name if env_name else var_name]
        except KeyError:
            raise ImproperlyConfigured("Set the %s environment variable." % var_name)
AWS_ACCESS_KEY_ID = get_env_variable("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_variable("AWS_SECRET_ACCESS_KEY")
AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = True

DEFAULT_FILE_STORAGE = 'mitchslist.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'mitchslist.aws.utils.StaticRootS3BotoStorage'
AWS_STORAGE_BUCKET_NAME = get_env_variable("S3_BUCKET_NAME")
S3DIRECT_REGION = 'us-west-2'
S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = { 
    'Expires': expires,
    'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}