from django.test import TestCase

from ..models import Content, Check
from .helpers import create_content, create_user

import os
from django.conf import settings
from boto3.session import Session
from botocore.exceptions import ClientError

test_file = 'cms/tests/test.mp4'
REGION = settings.S3DIRECT_REGION
AWS_ACCESS_KEY = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

def is_s3_exists(s3, bucket, filepath):
    try:
        s3.Object(bucket, filepath).load()
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise e
    else:
        return True

class ContentTest(TestCase):
    def test_if_content_check_deletion(self):
        """
        Contentが削除されたタイミングで
        関連付けられたCheckも同様に削除される。
        """
        c = create_content()
        u = create_user()
        ch = Check(user=u, content=c)
        ch.save()
        self.assertEqual(Check.objects.count(), 1)
        c.delete()
        self.assertEqual(Check.objects.count(), 0)

    def setup_s3(self, s3, bucket, key):
        """
        テスト用のファイルをS3にアップロードする。
        """
        if is_s3_exists(s3, BUCKET_NAME, key):
            s3.Object(BUCKET_NAME, key).delete()
        bucket.upload_file(test_file, key)

    def after_s3(self, s3, key):
        """
        テスト用のファイルをS3から削除する。
        """
        if is_s3_exists(s3, BUCKET_NAME, key):
            s3.Object(BUCKET_NAME, key).delete()

    def test_file_delete_when_content_deleted(self):
        """
        Contentレコードが削除されると同時にS3上にあるファイルも削除される。
        """
        test_file_basename = os.path.basename(test_file)
        test_key = 'test/' + test_file_basename
        session = Session(aws_access_key_id=AWS_ACCESS_KEY,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=REGION)
        s3 = session.resource('s3')
        bucket = s3.Bucket(BUCKET_NAME)

        self.setup_s3(s3, bucket, test_key)

        # test code
        dest = 'https://{region}.amazonaws.com/{bucket_name}/{test_key}'.format(
            region=REGION,
            bucket_name=BUCKET_NAME,
            test_key=test_key,
        )

        import urllib
        url = urllib.parse.urlparse(dest)[2].split('/')[2:]
        url = '/'.join(url)

        content = Content(title='delete_test', filepath=dest)
        content.save()
        content.delete()
        existance = is_s3_exists(s3, BUCKET_NAME, test_key)
        self.assertFalse(existance)

        self.after_s3(s3, test_key)
