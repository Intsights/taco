import unittest
import uuid

import taco.logger.logger
import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper

import taco.ref_count_manager.exceptions as ref_count_exceptions
import taco.ref_count_manager.ref_count_table_creation_config as ref_count_table_creation_config
import taco.ref_count_manager.ref_count_manager as ref_count_manager
import taco.aws_wrappers.dynamodb_wrapper.dynamodb_wrapper as dynamodb_wrapper_module


class TestRefCountManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = taco.logger.logger.get_logger('TestRuntimeConfigManager')
        cls._ssm_wrapper = ssm_wrapper.SSMWrapper(logger=cls._logger)

        # Create Run Time Config Table
        cls._table_name = 'test_ref_count_{0}'.format(uuid.uuid1())
        cls._dynamodb_wrapper = dynamodb_wrapper_module.DynamoDBWrapper(
            logger=cls._logger,
            aws_access_key=cls._ssm_wrapper.aws_access_key,
            aws_secret_key=cls._ssm_wrapper.aws_secret_key
        )
        cls._dynamodb_wrapper.create_table(
            ref_count_table_creation_config.RefCountTableCreation(table_name=cls._table_name)
        )
        cls._ref_count_manager = ref_count_manager.RefCountManager(cls._dynamodb_wrapper, table_name=cls._table_name)

    def _validate_update(self, update_method, unique_id, routing, expected_count):
        current_count = update_method(unique_id, routing)
        self.assertEqual(current_count['Attributes']['routing_counter'], expected_count)
        current_count = self._ref_count_manager.get_current_ref_count(unique_id, routing)
        self.assertEqual(current_count, expected_count)

    def test_increment(self):
        for _ in range(3):
            unique_id = str(uuid.uuid1())
            for expected_count in range(1, 10):
                self._validate_update(self._ref_count_manager.increament_count,
                                      unique_id,
                                      'routing_a',
                                      expected_count)

            for expected_count in range(1, 10):
                self._validate_update(self._ref_count_manager.increament_count,
                                      unique_id,
                                      'routing_b',
                                      expected_count)

    def test_decrease(self):
        for _ in range(3):
            unique_id = str(uuid.uuid1())
            for count in range(1, 10):
                self._validate_update(self._ref_count_manager.deccreament_count,
                                      unique_id,
                                      'routing_a',
                                      -count)

            for count in range(1, 10):
                self._validate_update(self._ref_count_manager.deccreament_count,
                                      unique_id,
                                      'routing_b',
                                      -count)

    def test_ref_counter_not_found(self):
        unique_id = str(uuid.uuid1())
        self.assertRaises(ref_count_exceptions.RefCounterException,
                          self._ref_count_manager.get_current_ref_count,
                          unique_id,
                          str(uuid.uuid1()))

        uuid_1 = str(uuid.uuid1())
        self._ref_count_manager.remove_counter(uuid_1, str(uuid.uuid1()))
        self._ref_count_manager.deccreament_count(uuid_1, str(uuid.uuid1()))
        self._ref_count_manager.increament_count(uuid_1, str(uuid.uuid1()))

    @classmethod
    def tearDownClass(cls):
        cls._ref_count_manager = None

        try:
            cls._dynamodb_wrapper.delete_table(cls._table_name)
        except Exception as exc:
            cls._logger.warn('Failed to delete table', table_name=cls._table_name, exc=exc)

        cls._dynamodb_wrapper = None


if __name__ == '__main__':
    unittest.main()
