import taco.common.exceptions


class S3Exception(taco.common.exceptions.DataDictException):
    pass


# --- bucket ---
class ListBucketException(S3Exception):
    def __init__(self, exc=None):
        super().__init__('Failed to list buckets', exc=exc)


class BucketException(S3Exception):
    def __init__(self, message, bucket_name, exc=None):
        super().__init__(message, data_dict={'bucket_name': bucket_name}, exc=exc)


class InvalidBucketException(BucketException):
    def __init__(self, bucket_name, exc=None):
        super().__init__('Invalid bucket', bucket_name=bucket_name, exc=exc)


class DeletingBucketException(BucketException):
    def __init__(self, bucket_name, exc=None):
        super().__init__('Failed to delete bucket', bucket_name=bucket_name, exc=exc)


class DeletingNoneEmptyBucketException(BucketException):
    def __init__(self, bucket_name, exc=None):
        super().__init__('According to user request, can not delete non empty bucket', bucket_name, exc=exc)


class CreatingBucketException(BucketException):
    def __init__(self, bucket_name, exc=None):
        super().__init__('Failed to create bucket', bucket_name=bucket_name, exc=exc)


# --- files ---
class FileException(S3Exception):
    def __init__(self, message, bucket_name, file_path, exc=None):
        super().__init__(message,
                         exc=exc,
                         data_dict={
                             'bucket_name': bucket_name,
                             'file_path': file_path
                         })


class GettingFileMetadataException(FileException):
    def __init__(self, bucket_name, file_path, exc=None):
        super().__init__('Failed to get file metadata', bucket_name=bucket_name, file_path=file_path, exc=exc)


class GettingHeadObjectException(FileException):
    def __init__(self, bucket_name, file_path, exc=None):
        super().__init__('Failed to get head object', bucket_name=bucket_name, file_path=file_path, exc=exc)


class GettingFileContentException(FileException):
    def __init__(self, bucket_name, file_path, exc=None):
        super().__init__('Failed to get file content', bucket_name=bucket_name, file_path=file_path, exc=exc)


class DeletingFileException(FileException):
    def __init__(self, bucket_name, file_path, exc=None):
        super().__init__('Failed to delete file', bucket_name=bucket_name, file_path=file_path, exc=exc)


class UpdatingFileMetadataException(FileException):
    def __init__(self, bucket_name, file_path, exc=None):
        super().__init__('Failed to update file metadata', bucket_name=bucket_name, file_path=file_path, exc=exc)


class UploadingFileContentException(FileException):
    def __init__(self, bucket_name, file_path, exc=None):
        super().__init__('Failed to upload file content', bucket_name=bucket_name, file_path=file_path, exc=exc)
