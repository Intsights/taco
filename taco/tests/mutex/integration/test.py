import uuid
import time
import unittest

import taco.logger.logger

import taco.aws_wrappers.dynamodb_wrapper.dynamodb_wrapper as dynamodb_wrapper_module
import taco.mutex.mutex as cloud_mutex
import taco.mutex.mutex_table_creation_config as mutex_table_creation_config
import taco.mutex.exceptions as mutex_exceptions
import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper

from . import consts as mutex_tests_consts


class TestMutex(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = taco.logger.logger.get_logger('TestCloudMutex')
        cls._ssm_wrapper = ssm_wrapper.SSMWrapper(logger=cls._logger)
        cls._dynamodb_wrapper = dynamodb_wrapper_module.DynamoDBWrapper(logger=cls._logger,
                                                                        aws_access_key=cls._ssm_wrapper.aws_access_key,
                                                                        aws_secret_key=cls._ssm_wrapper.aws_secret_key,
                                                                        region_name=mutex_tests_consts.DEFAULT_REGION)
        cls._mutex_table_name = 'mutex_{0}'.format(uuid.uuid1())
        cls._dynamodb_wrapper.create_table(
            mutex_table_creation_config.MutexTableCreation(table_name=cls._mutex_table_name)
        )

        cls._default_mutex_kwargs = {
            'logger': cls._logger,
            'table_name': cls._mutex_table_name,
            'dynamodb_wrapper': cls._dynamodb_wrapper
        }

    def test_simple_mutex(self):
        mutex_name = str(uuid.uuid1())
        mutex = cloud_mutex.CloudMutex(mutex_name, **self._default_mutex_kwargs)

        # Validate lock-release
        for _ in range(2):
            mutex.lock()
            mutex.release()

        # Test re-lcok from the same context (mutex name & holder)
        for _ in range(2):
            mutex.lock()

        # Test lock of same mutex by 2 different holders
        mutex_brother = cloud_mutex.CloudMutex(mutex_name, **self._default_mutex_kwargs)
        with self.assertRaises(mutex_exceptions.MutexLockFailedException):
            mutex_brother.lock()

        mutex.release()
        mutex_brother.lock()

    def test_mutex_ttl(self):
        mutex_name = str(uuid.uuid1())
        mutex = cloud_mutex.CloudMutex(mutex_name, ttl=mutex_tests_consts.TTL, **self._default_mutex_kwargs)
        mutex_brother = cloud_mutex.CloudMutex(mutex_name, ttl=mutex_tests_consts.TTL, **self._default_mutex_kwargs)

        mutex.lock()
        with self.assertRaises(mutex_exceptions.MutexLockFailedException):
            mutex_brother.lock()

        # Lock is valid for TTL_SECONDS so in order to test this TTL feature we should sleep TTL + epsilon
        time.sleep(mutex_tests_consts.TTL + mutex_tests_consts.ADDITIONAL_SLEEP_SECONDS)
        mutex_brother.lock()

    def test_enter_exit(self):
        mutex_name = str(uuid.uuid1())
        mutex_brother = cloud_mutex.CloudMutex(mutex_name, **self._default_mutex_kwargs)

        with cloud_mutex.CloudMutex(mutex_name, **self._default_mutex_kwargs):
            self.assertRaises(mutex_exceptions.MutexLockFailedException, mutex_brother.lock)

    @classmethod
    def tearDownClass(cls):
        try:
            cls._dynamodb_wrapper.delete_table(cls._mutex_table_name)

        except Exception as exc:
            cls._logger.warn('Failed to delete table', table_name=cls._mutex_table_name, exc=exc)

        cls._dynamodb_wrapper = None


if __name__ == '__main__':
    unittest.main()
