import time
import unittest
import uuid
import threading

from collections import namedtuple

import taco.logger.logger

from taco.tests.message_duplication_handler.integration import consts as message_duplication_handler_tests_consts

import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper
import taco.message_duplication_handler.message_duplication_handler as message_duplication_handler
import taco.aws_wrappers.dynamodb_wrapper.dynamodb_wrapper as dynamodb_wrapper_module
import taco.mutex.mutex_table_creation_config as mutex_table_creation_config


class TestAWSMessageDuplicationHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = taco.logger.logger.get_logger(cls.__name__)
        cls._mutex_table_name = 'mutex_{0}'.format(uuid.uuid1())
        cls._ssm_wrapper = ssm_wrapper.SSMWrapper(logger=cls._logger)
        cls._dynamodb_wrapper = dynamodb_wrapper_module.DynamoDBWrapper(
            logger=cls._logger,
            aws_access_key=cls._ssm_wrapper.aws_access_key,
            aws_secret_key=cls._ssm_wrapper.aws_secret_key,
            region_name=message_duplication_handler_tests_consts.DEFAULT_REGION
        )

        # Create the mutex table
        cls._dynamodb_wrapper.create_table(
            mutex_table_creation_config.MutexTableCreation(table_name=cls._mutex_table_name)
        )

    def test_basic_duplications(self):

        # Tested method
        @message_duplication_handler.message_duplication_handler(
            reprocess_timeout=message_duplication_handler_tests_consts.REPROCESS_TIMEOUT,
            mutex_table_name=self._mutex_table_name
        )
        def _my_sleep_lambda(logger, context):
            logger.info('Start my_sleep_lambda')
            context.executed_functions.append('my_sleep_lambda')
            time.sleep(message_duplication_handler_tests_consts.REPROCESS_TIMEOUT)
            logger.info('End my_sleep_lambda')

        executed_functions = []

        lambda_name = str(uuid.uuid1())
        request_id = str(uuid.uuid1())

        context = namedtuple('Context', 'function_name function_version aws_request_id executed_functions')

        for _ in range(3):
            threading.Thread(target=_my_sleep_lambda,
                             args=(self._logger, context(lambda_name, 1, request_id, executed_functions))).start()

        time.sleep(message_duplication_handler_tests_consts.REPROCESS_TIMEOUT * 3)
        self.assertEqual(len(executed_functions), 1)

        threading.Thread(target=_my_sleep_lambda,
                         args=(self._logger, context(lambda_name, 1, request_id, executed_functions))).start()
        time.sleep(message_duplication_handler_tests_consts.REPROCESS_TIMEOUT / 2)
        self.assertEqual(len(executed_functions), 2)


if __name__ == '__main__':
    unittest.main()
