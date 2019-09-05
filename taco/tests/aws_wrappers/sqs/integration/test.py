import time
import uuid
import unittest

import taco.tests.aws_wrappers.sqs.integration.consts as sqs_tests_consts

import taco.logger.logger

import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper
import taco.aws_wrappers.sqs_wrapper.sqs_wrapper as sqs_wrapper_module
import taco.aws_wrappers.sqs_wrapper.exceptions as sqs_exceptions
import taco.aws_wrappers.sqs_wrapper.consts as sqs_consts
import taco.aws_wrappers.sqs_wrapper.configs as sqs_configs


class TestSQS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = taco.logger.logger.get_logger(cls.__name__)
        cls._ssm_wrapper = ssm_wrapper.SSMWrapper(logger=cls._logger)
        cls._sqs_wrapper = sqs_wrapper_module.SQSWrapper(logger=cls._logger,
                                                         aws_access_key=cls._ssm_wrapper.aws_access_key,
                                                         aws_secret_key=cls._ssm_wrapper.aws_secret_key,
                                                         region_name=sqs_tests_consts.DEFAULT_REGION)
        cls._created_sqs = []

    # ------ Helpers ------
    def _wait_for_complete_queue_operation(self):

        # AWS.SimpleQueueService.QueueDeletedRecently exception is mitigated by waiting 1 minute thus this operation
        # should be considered as very slow
        self._logger.info('Sleep 60 seconds for completion of queue operation')
        time.sleep(60)

    def _create_sqs(self,
                    queue_name=None,
                    enable_dead_letter_queue=True,
                    visibility_timeout_seconds=1,
                    force_clean_queue=True,
                    max_receive_count=sqs_consts.DefaultQueueConfig.max_receive_count.value):
        if queue_name is None:
            queue_name = str(uuid.uuid1())

        creating_sqs_config = sqs_configs.SQSCreationConfig(queue_name,
                                                            enable_dead_letter_queue=enable_dead_letter_queue,
                                                            force_clean_queue=force_clean_queue,
                                                            visibility_timeout_seconds=visibility_timeout_seconds,
                                                            max_receive_count=max_receive_count)
        self._sqs_wrapper.create_queue(creating_sqs_config)
        self._wait_for_complete_queue_operation()

        self._created_sqs.append(creating_sqs_config.dlq_name)
        self._created_sqs.append(creating_sqs_config.queue_name)
        return queue_name, creating_sqs_config.dlq_name

    def _verify_no_queue(self, queue_name):
        with self.assertRaises(sqs_exceptions.SQSNonExistingQueueException):
            self._sqs_wrapper.get_queue_by_name(queue_name)

    # ------ Tests ------
    def test_list_queue(self):
        queue_name, dlq_name = self._create_sqs(enable_dead_letter_queue=True)
        sqs_names = [sqs_url.split('/')[-1] for sqs_url in self._sqs_wrapper.list_queues()]
        self.assertIn(queue_name, sqs_names)
        self.assertIn(dlq_name, sqs_names)

    def test_get_queue_by_name(self):
        with self.assertRaises(sqs_exceptions.SQSNonExistingQueueException):
            self._sqs_wrapper.get_queue_by_name(str(uuid.uuid1()))

        queue_name, dlq_name = self._create_sqs(enable_dead_letter_queue=True)
        self._sqs_wrapper.get_queue_by_name(queue_name)

    def test_create_delete_queues(self):

        queue_name, dlq_name = self._create_sqs(enable_dead_letter_queue=True)

        self._sqs_wrapper.delete_queue(queue_name, False)
        self._verify_no_queue(queue_name)

        self._sqs_wrapper.delete_queue(queue_name, True)
        self._wait_for_complete_queue_operation()
        self._verify_no_queue(dlq_name)

    def test_create_queue_twice(self):
        queue_name, dlq_name = self._create_sqs(enable_dead_letter_queue=True)
        self._sqs_wrapper.send_message(queue_name, sqs_tests_consts.JSON_DATA_TEST)

        # Create queue with different params
        with self.assertRaises(sqs_exceptions.SQSCreateExistingQueueParamsErrorException):
            self._create_sqs(queue_name=queue_name, visibility_timeout_seconds=5, force_clean_queue=False) ##

        # Dummy create queue
        self._create_sqs(queue_name=queue_name, visibility_timeout_seconds=1, force_clean_queue=False)

        read_data_set = self._sqs_wrapper.read_messages(queue_name, False)
        self.assertEqual(len(read_data_set), 1)

        self._create_sqs(queue_name=queue_name, force_clean_queue=True, enable_dead_letter_queue=False)
        read_data_set = self._sqs_wrapper.read_messages(queue_name, False)
        self.assertEqual(read_data_set, [])

    def test_delete_invalid_queue(self):
        for _ in range(3):
            self._sqs_wrapper.delete_queue(str(uuid.uuid1()))

    def test_send_receive_valid_messages(self):
        queue_name, dlq_name = self._create_sqs(visibility_timeout_seconds=1, max_receive_count=1)

        for _ in range(3):
            self._sqs_wrapper.send_message(queue_name, sqs_tests_consts.JSON_DATA_TEST)

        self._sqs_wrapper.read_messages(queue_name, delete_after_receive=True, messages_limit=1)

        read_data_set_1 = self._sqs_wrapper.read_messages(queue_name, delete_after_receive=False, messages_limit=2)
        self.assertEqual(len(read_data_set_1), 2)

        for read_data in read_data_set_1:
            self.assertEqual(read_data.data, sqs_tests_consts.RAW_DATA_TEST)

        read_data_set_2 = self._sqs_wrapper.read_messages(queue_name, delete_after_receive=True, messages_limit=5)
        for read_data_1, read_data_2 in zip(read_data_set_1, read_data_set_2):
            self.assertEqual(read_data_1.data, read_data_2.data)

        read_data_set_3 = self._sqs_wrapper.read_messages(queue_name, messages_limit=1)
        self.assertListEqual(read_data_set_3, [])

    def test_send_receive_invalid_data_meesage(self):
        queue_name, dlq_name = self._create_sqs()
        self._sqs_wrapper.send_message(queue_name, sqs_tests_consts.RAW_DATA_TEST)
        read_data_set = self._sqs_wrapper.read_messages(queue_name)
        self.assertEqual(len(read_data_set), 1)

    def test_send_delayed_meesage(self):
        queue_name, dlq_name = self._create_sqs()
        self._sqs_wrapper.send_message(queue_name,
                                       sqs_tests_consts.JSON_DATA_TEST,
                                       delay_seconds=sqs_tests_consts.MESSAGE_DELAY)

        read_data_set = self._sqs_wrapper.read_messages(queue_name)
        self.assertListEqual(read_data_set, [])

        self._logger.debug('Waiting for delay to pass')
        time.sleep(sqs_tests_consts.MESSAGE_DELAY * 2)
        read_data_set = self._sqs_wrapper.read_messages(queue_name)
        self.assertEqual(read_data_set[0].data, sqs_tests_consts.RAW_DATA_TEST)

    def test_clear_queue(self):

        # Create sqs
        queue_name, dlq_name = self._create_sqs()

        # Ensure read_messages with delete_after_receive=False is ok
        self._sqs_wrapper.send_message(queue_name, sqs_tests_consts.JSON_DATA_TEST)
        read_data_set_2 = self._sqs_wrapper.read_messages(queue_name, delete_after_receive=False)
        self.assertEqual(read_data_set_2[0].data, sqs_tests_consts.RAW_DATA_TEST)

        time.sleep(sqs_tests_consts.DEFAULT_SQS_VISIBILITY_TIMEOUT)
        read_data_set_3 = self._sqs_wrapper.read_messages(queue_name, delete_after_receive=False)
        self.assertEqual(read_data_set_3[0].data, sqs_tests_consts.RAW_DATA_TEST)

        # Clear queue (containing one message)
        self._sqs_wrapper.clear_queue(queue_name)
        read_data_set_4 = self._sqs_wrapper.read_messages(queue_name)
        self.assertListEqual(read_data_set_4, [])

        # This should trigger 'Purge in progress' exception flow
        for _ in range(2):
            self._sqs_wrapper.clear_queue(queue_name)

    def test_dead_letter_queue(self):
        queue_name, dlq_name = self._create_sqs()

        # Push message to queue
        self._sqs_wrapper.send_message(queue_name, sqs_tests_consts.JSON_DATA_TEST)

        # Pop message max_receive_count times to apply dlq transformation
        for _ in range(sqs_consts.DefaultQueueConfig.max_receive_count.value):
            read_data_set = self._sqs_wrapper.read_messages(queue_name, False, messages_limit=1)
            self._logger.debug('Read data', read_data_set=read_data_set)
            self.assertEqual(read_data_set[0].data, sqs_tests_consts.RAW_DATA_TEST)

            # Ensure we pass visibility timeout
            time.sleep(sqs_tests_consts.VISIBILITY_TIMEOUT_SECONDS)

        # Pop empty queue
        read_data_set = self._sqs_wrapper.read_messages(queue_name, False)
        self.assertEqual(read_data_set, [])

        # Pop message from dlq
        read_data_set = self._sqs_wrapper.read_messages(dlq_name, False)

        self.assertEqual(len(read_data_set), 1)
        self.assertEqual(read_data_set[0].data, sqs_tests_consts.RAW_DATA_TEST)

    @classmethod
    def tearDownClass(cls):
        for queue_name in cls._created_sqs:
            try:

                cls._sqs_wrapper.clear_queue(queue_name)
                cls._sqs_wrapper.delete_queue(queue_name=queue_name)

            except Exception as exc:
                cls._logger.warn('Failed to delete queue', queue_name=queue_name, exc=exc)

        cls._sqs_wrapper = None
        cls._ssm_wrapper = None


if __name__ == '__main__':
    unittest.main()
