from storages.backends.s3boto3 import S3Boto3Storage
class MediaStorage(S3Boto3Storage):
    location = 'django_test_space/media'
    file_overwrite = True