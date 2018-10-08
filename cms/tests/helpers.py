from django.contrib.auth.models import User
from ..models import Content

def create_user(username='test@example.com', password='test'):
    u = User(username=username)
    u.set_password(password)
    u.save()
    return u

def login(client):
    """
    Login as normal user (not admin or staff)
    """
    create_user()
    return client.login(username='test@example.com', password='test')

def create_content(title='test', filepath='http://example.com/something.mp4', thumb=False):
    c = Content(title=title, filepath=filepath, thumb=thumb)
    c.save()
    return c

from django.conf import settings
from boto3.session import Session
from botocore.exceptions import ClientError
import os

REGION = settings.S3DIRECT_REGION
BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
SESSION = Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                  region_name=REGION)
S3 = SESSION.resource('s3')
BUCKET = S3.Bucket(BUCKET_NAME)
BASE_KEY = 'test/'
BASE_URL = 'https://s3-' + REGION + '.amazonaws.com/' + BUCKET_NAME + '/'

def s3_key(filename):
    """
    テスト用のkeyを生成して返す。
    """
    return BASE_KEY + os.path.basename(filename)

def is_s3_exists(filename):
    key = s3_key(filename)
    try:
        S3.Object(BUCKET_NAME, key).load()
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise e
    else:
        return True

def s3_delete(filename):
    """
    S3上からファイルを削除する。
    """
    key = s3_key(filename)
    if is_s3_exists(filename):
        S3.Object(BUCKET_NAME, key).delete()

def s3_upload(filename):
    """
    S3にファイルをアップロードする。その後ACLを書き換え、Publicに変更する。
    """
    key = s3_key(filename)
    s3_delete(filename)
    BUCKET.upload_file(filename, key)
    acl = S3.ObjectAcl(BUCKET_NAME, key)
    acl.put(ACL='public-read')
    return BASE_URL + key
