import os
import urllib
import subprocess

from boto3.session import Session
from botocore.exceptions import ClientError

from django.conf import settings

def generate_thumbnail(title, filepath):
    """
    10秒の位置で320x240のサムネイルを作成する場合:
      ffmpeg -i #{VIDEO}.mp4 -ss 10 -vframes 1 -f image2 -s 320x240 #{VIDEO}.jpg
    """
    thumb = '/tmp/thumb-{}.jpg'.format(title)
    fileurl = urllib.parse.quote(filepath, safe=':/')
    ffmpeg = 'ffmpeg -y -i "{filepath}" -ss 0 -vframes 1 -f image2 -s 320x240 {thumb}'.format(
        filepath=fileurl, thumb=thumb
    )
    subprocess.call(ffmpeg, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return thumb

def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        return bytes_or_str.decode()
    else:
        return bytes_or_str

def uri2key(uri):
    parts = urllib.parse.urlparse(uri)
    path = parts.path
    path = to_str(path)
    paths = path.split('/')
    splited_keys = paths[2:]
    return '/'.join(splited_keys) if splited_keys else ''

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
    return 'https://s3-{region}.amazonaws.com/{bucket}/{key}'.format(
        region=settings.S3DIRECT_REGION,
        bucket=settings.AWS_STORAGE_BUCKET_NAME,
        key=key)
