import botocore.exceptions

import taco.common.logger_based_object

from taco import aws_wrappers as boto3_helpers
import taco.boto3.boto_config as boto_config
import taco.boto3.boto3_helpers as boto3_helpers

from . import consts as s3_consts
from . import exceptions as s3_exceptions


class S3Wrapper(taco.common.logger_based_object.LoggerBasedObject):

    def __init__(self,
                 region_name=s3_consts.DEFAULT_REGION,
                 resource_config=s3_consts.DEFAULT_RESOURCE_CONFIG,
                 aws_access_key=None,
                 aws_secret_key=None,
                 logger=None):
        super().__init__(logger=logger)
        self._default_region_name = region_name
        self._s3_client, self._s3_resource = boto3_helpers.get_client_resource(aws_access_key,
                                                                               aws_secret_key,
                                                                               boto_config.Boto3Resources.s3.value,
                                                                               self._default_region_name,
                                                                               config=resource_config)

    def list_buckets(self):
        try:
            return [bucket.name for bucket in self._s3_resource.buckets.all()]

        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(s3_exceptions.ListBucketException, exc=exc)

    def is_bucket_valid(self, bucket_name):
        """
        Check if the bucket exist and if the user have permission to access the bucket
        """
        try:
            self._s3_client.head_bucket(Bucket=bucket_name)

        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(s3_exceptions.InvalidBucketException, bucket_name=bucket_name, exc=exc)

    def delete_bucket(self, bucket_name, delete_non_empty_bucket=True):
        try:
            bucket = self._s3_resource.Bucket(bucket_name)
            bucket_objects = bucket.objects.all()
            if sum(1 for _ in bucket_objects) != 0:
                if not delete_non_empty_bucket:
                    self._logger.log_and_raise(s3_exceptions.DeletingNoneEmptyBucketException, bucket_name=bucket_name)

                objects_deletion_output = bucket_objects.delete()
                self._logger.debug('Deleted bucket objects',
                                   deletion_output=objects_deletion_output)

            bucket.delete()
            # bucket.wait_until_not_exists()

        except botocore.exceptions.ClientError as exc:
            if boto3_helpers.is_exception_type(exc, s3_consts.IgnoredErrors.bucket_deletion.value):
                self._logger.debug('Bucket does not exist, skip deletions', bucket_name=bucket_name)
                return

            self._logger.log_and_raise(s3_exceptions.DeletingBucketException, bucket_name=bucket_name, exc=exc)

    def create_bucket(self, bucket_name, region_name=None):
        if region_name is None:
            region_name = self._default_region_name

        try:
            bucket = self._s3_resource.create_bucket(Bucket=bucket_name,
                                                     ACL='private',
                                                     CreateBucketConfiguration={'LocationConstraint': region_name})
            # bucket.wait_until_exists()

        except botocore.exceptions.ClientError as exc:
            if boto3_helpers.is_exception_type(exc, s3_consts.IgnoredErrors.bucket_creation.value):
                self._logger.debug('Bucket already exist', bucket_name=bucket_name)
                return

            self._logger.log_and_raise(s3_exceptions.CreatingBucketException, bucket_name=bucket_name, exc=exc)

    def upload_data_to_file(self,
                            bucket_name,
                            file_path,
                            data='',
                            metadata=None,
                            content_type=s3_consts.ContentType.default.value):

        # Note: All metadata values must be in lower case
        if metadata is None:
            metadata = {}

        s3_object = self._s3_resource.Object(bucket_name, file_path)
        new_metadata = metadata
        if self.file_exists(bucket_name, file_path):
            new_metadata = s3_object.metadata
            new_metadata.update(metadata)

        try:
            s3_object.put(Body=data, Metadata=new_metadata, ContentType=content_type)
            # s3_object.wait_until_exists()

        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(s3_exceptions.UploadingFileContentException,
                                       bucket_name=bucket_name,
                                       file_path=file_path,
                                       exc=exc)

    def update_file_metadata(self, bucket_name, file_path, new_metadata):
        try:
            s3_object = self._s3_resource.Object(bucket_name, file_path)
            original_metadata = s3_object.metadata
            original_metadata.update(new_metadata)
            s3_object.copy_from(CopySource={'Bucket': bucket_name, 'Key': file_path},
                                Metadata=original_metadata,
                                MetadataDirective='REPLACE')

        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(s3_exceptions.UpdatingFileMetadataException,
                                       bucket_name=bucket_name,
                                       file_path=file_path,
                                       exc=exc)

    def delete_file(self, bucket_name, file_path):
        try:
            requested_object = self._s3_resource.Object(bucket_name, file_path)
            requested_object.delete()
            # requested_object.wait_until_not_exists()

        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(s3_exceptions.DeletingFileException,
                                       bucket_name=bucket_name,
                                       file_path=file_path,
                                       exc=exc)

    def get_file_metadata(self, bucket_name, file_path):
        try:
            return self._s3_resource.Object(bucket_name, file_path).metadata

        except botocore.exceptions.ClientError as exc:
            if boto3_helpers.is_exception_type(exc, s3_consts.IgnoredErrors.object_missing.value):
                self._logger.log_and_raise(s3_exceptions.GettingFileMetadataException,
                                           bucket_name=bucket_name,
                                           file_path=file_path,
                                           exc=exc)

    def file_exists(self, bucket_name, file_path):
        return self.get_head_object(bucket_name, file_path) is not None

    def get_file_data(self, bucket_name, file_path):
        try:
            requested_object = self._s3_resource.Object(bucket_name, file_path)
            streaming_body = requested_object.get().get('Body')
            if streaming_body is not None:
                return streaming_body.read()

        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(s3_exceptions.GettingFileContentException,
                                       bucket_name=bucket_name,
                                       file_path=file_path,
                                       exc=exc)

    def get_head_object(self, bucket_name, file_path):
        try:
            return self._s3_client.head_object(Bucket=bucket_name, Key=file_path)

        except botocore.exceptions.ClientError as exc:
            if boto3_helpers.is_exception_type(exc, s3_consts.IgnoredErrors.object_missing.value):
                return

            self._logger.log_and_raise(s3_exceptions.GettingHeadObjectException,
                                       bucket_name=bucket_name,
                                       file_path=file_path,
                                       exc=exc)

