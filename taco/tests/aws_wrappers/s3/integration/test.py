import unittest
import unittest.mock
import uuid
import time

import taco.logger.logger as aws_intsights_logger

import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper
import taco.aws_wrappers.s3_wrapper.s3_wrapper as s3_wrapper
import taco.aws_wrappers.s3_wrapper.exceptions as s3_exceptions

from taco.tests.aws_wrappers.s3.integration import consts as s3_test_consts


class TestS3Wrapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = aws_intsights_logger.get_logger('test_s3_wrapper')
        cls._ssm_wrapper = ssm_wrapper.SSMWrapper(logger=cls._logger)
        cls._s3_wrapper = s3_wrapper.S3Wrapper(logger=cls._logger,
                                               aws_access_key=cls._ssm_wrapper.aws_access_key,
                                               aws_secret_key=cls._ssm_wrapper.aws_secret_key)

    def setUp(self):
        self._created_buckets = []

    def _create_bucket_and_verify_its_existence(self, bucket_name=None):
        if bucket_name is None:
            bucket_name = str(uuid.uuid1())

        self._s3_wrapper.create_bucket(bucket_name, region_name=s3_test_consts.DEFAULT_REGION)
        self.assertIn(bucket_name, self._s3_wrapper.list_buckets())
        self._created_buckets.append(bucket_name)
        self._logger.debug('Created new bucket', bucket_name=bucket_name)
        return bucket_name

    def _upload_download_file_and_validate_its_content(self,
                                                       bucket_name,
                                                       file_path=None,
                                                       data=s3_test_consts.FILE_DATA,
                                                       metadata=s3_test_consts.DEFAULT_METADATA,
                                                       expected_metadata=None):
        if file_path is None:
            file_path = str(uuid.uuid1())

        if expected_metadata is None:
            expected_metadata = metadata

        self._s3_wrapper.upload_data_to_file(bucket_name, file_path, data, metadata)
        self.assertEqual(self._s3_wrapper.get_file_data(bucket_name, file_path).decode(), data)
        self.assertDictEqual(self._s3_wrapper.get_file_metadata(bucket_name, file_path), expected_metadata)
        return file_path

    def test_create_a_bucket(self):

        # Create the same bucket multiple times
        self._s3_wrapper._logger.debug = unittest.mock.MagicMock()
        bucket_name = str(uuid.uuid1())
        for _ in range(2):
            self._create_bucket_and_verify_its_existence(bucket_name=bucket_name)

        self._s3_wrapper._logger.debug.called_with(s3_test_consts.BUCKET_ALREADY_EXISTS_ERROR_MESSGAE)

    def test_bucket_deletion(self):

        # Deleting non existing bucket
        self._s3_wrapper.delete_bucket(str(uuid.uuid1()))

        bucket_name = self._create_bucket_and_verify_its_existence()
        for _ in range(2):
            self._s3_wrapper.delete_bucket(bucket_name)

        # upload file to a bucket and verify wrapper does not delete the bucket
        bucket_name = self._create_bucket_and_verify_its_existence()
        file_name = str(uuid.uuid1())
        self._s3_wrapper.upload_data_to_file(bucket_name, file_name, s3_test_consts.FILE_DATA)
        self.assertRaises(s3_exceptions.DeletingNoneEmptyBucketException,
                          self._s3_wrapper.delete_bucket,
                          bucket_name,
                          delete_non_empty_bucket=False)

        # verify file exists
        self.assertEqual(s3_test_consts.FILE_DATA, self._s3_wrapper.get_file_data(bucket_name, file_name).decode())

        # Delete non empty bucket
        self._s3_wrapper.delete_bucket(bucket_name, delete_non_empty_bucket=True)
        time.sleep(10)
        self.assertRaisesRegex(s3_exceptions.GettingFileContentException,
                               s3_test_consts.BUCKET_MISSING_ERROR_MESSAGE,
                               self._s3_wrapper.get_file_data,
                               bucket_name,
                               file_name)

    def test_file_upload(self):

        # test uploading a file to a non existing dir/bucket
        bucket_name = str(uuid.uuid1())
        file_path = str(uuid.uuid1())
        self.assertRaisesRegex(s3_exceptions.UploadingFileContentException,
                               s3_test_consts.BUCKET_MISSING_ERROR_MESSAGE,
                               self._s3_wrapper.upload_data_to_file,
                               bucket_name,
                               file_path,
                               s3_test_consts.FILE_DATA)

        bucket_name = self._create_bucket_and_verify_its_existence()

        # test uploading a file with metatata
        file_path = self._upload_download_file_and_validate_its_content(bucket_name)

        # test updating an existing file
        self._upload_download_file_and_validate_its_content(bucket_name,
                                                            file_path=file_path,
                                                            data=s3_test_consts.ALTERNATIVE_FILE_DATA,
                                                            metadata=s3_test_consts.ALTERNATIVE_METADATA,
                                                            expected_metadata=s3_test_consts.All_METADATA)

    def test_file_download(self):

        # Download a non existing file
        self.assertRaisesRegex(s3_exceptions.GettingFileContentException,
                               s3_test_consts.BUCKET_MISSING_ERROR_MESSAGE,
                               self._s3_wrapper.get_file_data,
                               str(uuid.uuid1()),
                               str(uuid.uuid1()))

        bucket_name = self._create_bucket_and_verify_its_existence()
        self.assertRaisesRegex(s3_exceptions.GettingFileContentException,
                               s3_test_consts.FILE_MISSING_ERROR_MESSAGE,
                               self._s3_wrapper.get_file_data,
                               bucket_name,
                               str(uuid.uuid1()))

        # Test file download
        self._upload_download_file_and_validate_its_content(bucket_name)

    def test_file_deletion(self):

        # test deleting non existing file
        file_path = str(uuid.uuid1())
        bucket_name = str(uuid.uuid1())
        self.assertRaisesRegex(s3_exceptions.DeletingFileException,
                               s3_test_consts.BUCKET_MISSING_ERROR_MESSAGE,
                               self._s3_wrapper.delete_file,
                               bucket_name,
                               file_path)

        self._create_bucket_and_verify_its_existence(bucket_name=bucket_name)
        self._upload_download_file_and_validate_its_content(bucket_name, file_path)
        self._s3_wrapper.delete_file(bucket_name, file_path)
        self.assertFalse(self._s3_wrapper.file_exists(bucket_name, file_path))

    def test_list_buckets(self):
        pre_bucket_creation_output = self._s3_wrapper.list_buckets()
        bucket_name = self._create_bucket_and_verify_its_existence()
        post_bucket_creation_output = self._s3_wrapper.list_buckets()

        self.assertSetEqual(set(post_bucket_creation_output) - set(pre_bucket_creation_output), set([bucket_name]))

    def test_is_bucket_valid(self):
        self.assertRaisesRegex(s3_exceptions.InvalidBucketException,
                               s3_test_consts.NOT_FOUND_ERROR_MESSAGE,
                               self._s3_wrapper.is_bucket_valid,
                               str(uuid.uuid1()))
        bucket_name = self._create_bucket_and_verify_its_existence()
        self._s3_wrapper.is_bucket_valid(bucket_name)

    def test_update_file_metadata(self):
        bucket_name = self._create_bucket_and_verify_its_existence()
        file_path = self._upload_download_file_and_validate_its_content(bucket_name)

        self._s3_wrapper.update_file_metadata(bucket_name, file_path, s3_test_consts.ALTERNATIVE_METADATA)
        self.assertDictEqual(s3_test_consts.All_METADATA, self._s3_wrapper.get_file_metadata(bucket_name, file_path))
        self.assertEqual(self._s3_wrapper.get_file_data(bucket_name, file_path).decode(), s3_test_consts.FILE_DATA)

    def test_get_file_metadata_of_non_existing_objects(self):
        self.assertRaisesRegex(s3_exceptions.GettingFileMetadataException,
                               s3_test_consts.NOT_FOUND_ERROR_MESSAGE,
                               self._s3_wrapper.get_file_metadata,
                               str(uuid.uuid1()),
                               str(uuid.uuid1()))

        bucket_name = self._create_bucket_and_verify_its_existence()
        self.assertRaisesRegex(s3_exceptions.GettingFileMetadataException,
                               s3_test_consts.NOT_FOUND_ERROR_MESSAGE,
                               self._s3_wrapper.get_file_metadata,
                               bucket_name,
                               str(uuid.uuid1()))

    def tearDown(self):
        for bucket_name in self._created_buckets:
            try:
                self._s3_wrapper.delete_bucket(bucket_name, delete_non_empty_bucket=TypeError)
                self.assertNotIn(bucket_name, self._s3_wrapper.list_buckets())
                self._logger.debug('Deleted bucket', bucket_name=bucket_name)

            except s3_exceptions.DeletingBucketException as exc:
                self._logger.warn('Failed to delete bucket', bucket_name=bucket_name, exc=exc)

        self._s3_wrapper = None


if __name__ == '__main__':
    unittest.main()
