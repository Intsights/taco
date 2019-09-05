import unittest
import uuid

import taco.logger.logger

import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper

import taco.s3_config_manager.exceptions as runtime_config_manager_exceptions
import taco.s3_config_manager.runtime_config_manager.runtime_config_manager as aws_runtime_config_manager
import taco.s3_config_manager.runtime_config_manager.consts as runtime_config_consts
import taco.aws_wrappers.s3_wrapper.s3_wrapper as s3_wrapper_module

from . import consts as runtime_config_test_consts


class TestRuntimeConfigManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = taco.logger.logger.get_logger('TestRuntimeConfigManager')
        cls._ssm_wrapper = ssm_wrapper.SSMWrapper(logger=cls._logger)
        
        cls._s3_wrapper = s3_wrapper_module.S3Wrapper(
            logger=cls._logger,
            aws_access_key=cls._ssm_wrapper.aws_access_key,
            aws_secret_key=cls._ssm_wrapper.aws_secret_key,
        )

        cls._bucket_name = str(uuid.uuid1())
        cls._s3_wrapper.create_bucket(cls._bucket_name)
        cls._s3_wrapper.upload_data_to_file(cls._bucket_name,
                                            file_path=runtime_config_consts.RUNTIME_CONFIG_FILE_NAME,
                                            data=runtime_config_test_consts.run_time_config)
        cls._runtime_config_manager = aws_runtime_config_manager.RuntimeConfigManager(
            cls._s3_wrapper,
            bucket_name=cls._bucket_name
        )

    def test_s3_bucket_runtime_config_read(self):
        resource_name = runtime_config_test_consts.TestConfigKeys.s3.value
        resource_value = runtime_config_test_consts.TestConfigValues.s3.value
        self.assertEqual(self._runtime_config_manager.get_bucket(resource_name), resource_value)

    def test_sqs_queue_runtime_config_read(self):
        resource_name = runtime_config_test_consts.TestConfigKeys.sqs.value
        resource_value = runtime_config_test_consts.TestConfigValues.sqs.value
        self.assertEqual(self._runtime_config_manager.get_sqs_queue(resource_name), resource_value)

    def test_generic_data_runtime_config_read(self):
        resource_name = runtime_config_test_consts.TestConfigKeys.generic_data.value
        resource_value = runtime_config_test_consts.TestConfigValues.generic_data.value
        self.assertEqual(self._runtime_config_manager.get_generic_data(resource_name), resource_value)

    def test_a_get_invalid_resource(self):
        resource_name = str(uuid.uuid1())
        self.assertRaises(runtime_config_manager_exceptions.MissingConfig,
                          self._runtime_config_manager.get_generic_data, resource_name)

    @classmethod
    def tearDownClass(cls):
        cls._runtime_config_manager = None
        cls._s3_wrapper.delete_bucket(cls._bucket_name)


if __name__ == "__main__":
    unittest.main()
