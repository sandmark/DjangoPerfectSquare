import os
import urllib
import hashlib

from boto3.session import Session
from botocore.exceptions import ClientError

from django.conf import settings

def uri2key(uri):
    parts = urllib.parse.urlparse(uri)[2].split('/')[2:]
    return '/'.join(parts) if parts else ''

def connect_s3():
    return Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                   region_name=settings.S3DIRECT_REGION).resource('s3')

def is_key_exists(key):
    s3 = connect_s3()
    try:
        s3.Object(settings.AWS_STORAGE_BUCKET_NAME, key).load()
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise e
    else:
        return True

def s3_delete_key(key):
    s3 = connect_s3()
    s3.Object(settings.AWS_STORAGE_BUCKET_NAME, key).delete()

def s3_upload_thumbnail(filename):
    s3 = connect_s3()
    key = 'thumbnails/' + os.path.basename(filename)
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    bucket.upload_file(filename, key)
    acl = s3.ObjectAcl(settings.AWS_STORAGE_BUCKET_NAME, key)
    acl.put(ACL='public-read')
    return 'https://s3-{region}.amazonaws.com/{bucket}{key}'.format(
        region=settings.S3DIRECT_REGION,
        bucket=settings.AWS_STORAGE_BUCKET_NAME,
        key=key)

def make_hash(ustring):
    h = hashlib.new('sha3-256')
    h.update(ustring.encode('unicode-escape'))
    return h.hexdigest()
