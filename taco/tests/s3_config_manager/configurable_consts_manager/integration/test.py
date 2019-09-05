import unittest
import uuid

import taco.logger.logger

import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper

import taco.aws_wrappers.s3_wrapper.s3_wrapper as s3_wrapper_module
import taco.s3_config_manager.configurable_consts_manager.configurable_consts_manager as aws_configurable_consts_manager
import taco.s3_config_manager.exceptions as configurable_consts_manager_exceptions

from . import consts as configurable_consts_manager_test_consts


class TestConfigurableConstsgManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = taco.logger.logger.get_logger('TestConfigurableConstsgManager')
        cls._ssm_wrapper = ssm_wrapper.SSMWrapper(logger=cls._logger)
        
        cls._s3_wrapper = s3_wrapper_module.S3Wrapper(
            logger=cls._logger,
            aws_access_key=cls._ssm_wrapper.aws_access_key,
            aws_secret_key=cls._ssm_wrapper.aws_secret_key,
        )

        cls._bucket_name = str(uuid.uuid1())
        cls._file_path = configurable_consts_manager_test_consts.TestConfigValues.consts_file_path.value
        cls._s3_wrapper.create_bucket(cls._bucket_name)
        cls._s3_wrapper.upload_data_to_file(cls._bucket_name,
                                            file_path=cls._file_path,
                                            data=configurable_consts_manager_test_consts.config)

        cls._configurable_consts_manager = aws_configurable_consts_manager.ConfigurableConstsManager(
            cls._s3_wrapper,
            cls._file_path,
            cls._bucket_name
        )

    def test_get_valid_consts(self):
        self.assertEqual(
            self._configurable_consts_manager.get_const(
                configurable_consts_manager_test_consts.TestConsts.my_const.name),
                configurable_consts_manager_test_consts.TestConsts.my_const.value
        )

    def test_get_invalid_const(self):
        const_name = str(uuid.uuid1())
        self.assertRaises(configurable_consts_manager_exceptions.MissingConfig,
                          self._configurable_consts_manager.get_const, const_name)
                          
    def test_get_invalid_const_file(self):
        const_file_path = str(uuid.uuid1())
        with self.assertRaises(configurable_consts_manager_exceptions.CorruptedConfigFile):
            aws_configurable_consts_manager.ConfigurableConstsManager(
                self._s3_wrapper,
                self._configurable_consts_manager,
                const_file_path)

    def test_get_corrupted_json_const_file(self):
        const_file_path = configurable_consts_manager_test_consts.TestConfigValues.corrupted_json_file_path.value
        with self.assertRaises(configurable_consts_manager_exceptions.CorruptedConfigFile):
            aws_configurable_consts_manager.ConfigurableConstsManager(
                self._s3_wrapper,
                self._configurable_consts_manager,
                const_file_path)
        

    @classmethod
    def tearDownClass(cls):
        cls._configurable_consts_manager = None
        cls._s3_wrapper.delete_bucket(cls._bucket_name)



if __name__ == "__main__":
    unittest.main()
