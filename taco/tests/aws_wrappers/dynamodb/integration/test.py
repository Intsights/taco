import unittest
import uuid
import unittest.mock
import copy
import time

import taco.logger.logger

import taco.aws_wrappers.auto_scaler_wrapper.auto_scaler_wrapper as auto_scaler_wrapper
import taco.aws_wrappers.dynamodb_wrapper.dynamodb_wrapper as dynamodb_wrapper
import taco.aws_wrappers.dynamodb_wrapper.consts as dynamodb_consts
import taco.aws_wrappers.dynamodb_wrapper.exceptions as dynamodb_exceptions
import taco.aws_wrappers.dynamodb_wrapper.condition as dynamodb_conditions
import taco.aws_wrappers.dynamodb_wrapper.table_creation_config as table_creation_config
import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper
from taco.tests.aws_wrappers.dynamodb.integration import consts as dynamodb_test_consts


class TestDynamoDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = taco.logger.logger.get_logger('TestDynamoDB')
        cls._ssm_wrapper = ssm_wrapper.SSMWrapper(logger=cls._logger)
        cls._auto_scaler = auto_scaler_wrapper.AutoScalerWrapper(logger=cls._logger,
                                                                 aws_access_key=cls._ssm_wrapper.aws_access_key,
                                                                 aws_secret_key=cls._ssm_wrapper.aws_secret_key)
        cls._dynamodb_wrapper = dynamodb_wrapper.DynamoDBWrapper(logger=cls._logger,
                                                                 aws_access_key=cls._ssm_wrapper.aws_access_key,
                                                                 aws_secret_key=cls._ssm_wrapper.aws_secret_key,
                                                                 region_name=dynamodb_test_consts.DEFAULT_REGION,
                                                                 auto_scaler=cls._auto_scaler)
        cls._table_list = []

    def _create_table(self, test_table_name, attribute_definitions=None, primary_keys=None, auto_scale=False):

        if attribute_definitions is None:
            attribute_definitions = dynamodb_test_consts.ATTRIBUTE_DEFINITIONS

        if primary_keys is None:
            primary_keys = dynamodb_test_consts.PRIMARY_KEYS

        self._dynamodb_wrapper.create_table(
            table_creation_config.TableCreationConfig(
                test_table_name, primary_keys, attribute_definitions),
            auto_scale=auto_scale
        )

    def _create_table_and_verify_its_existness(self, auto_scale=False):
        test_table_name = str(uuid.uuid1())
        previous_existing_tables = self._dynamodb_wrapper.list_tables()
        self.assertNotIn(test_table_name, previous_existing_tables)
        self._table_list.append(test_table_name)
        self._create_table(test_table_name, auto_scale=auto_scale)

        for i in range(10):
            if test_table_name in self._dynamodb_wrapper.list_tables():
                return test_table_name

            time.sleep(5)

        raise Exception('Failed to create a table')

    def _get_response_content(self, get_requests):
        response = self._dynamodb_wrapper.batch_get(get_requests)
        return response[dynamodb_test_consts.RESPONSE_KEY_NAME][get_requests[0]]

    def test_list_tables(self):
        self._create_table_and_verify_its_existness()

    def test_create_table(self):

        scale_table_name = self._create_table_and_verify_its_existness(
            auto_scale=True)

        # create table with the same name
        table_name = self._create_table_and_verify_its_existness()
        origin_logger = self._dynamodb_wrapper._logger
        self._dynamodb_wrapper._logger = unittest.mock.MagicMock()
        self._create_table(test_table_name=table_name)
        self._dynamodb_wrapper._logger.called_with(
            dynamodb_test_consts.TABLE_ALREADY_EXISTS_MESSAGE)
        self._dynamodb_wrapper._logger = origin_logger

        # create table with mismatch configs
        self.assertRaises(dynamodb_exceptions.CreatingTableWithInvalidParams,
                          self._create_table,
                          table_name,
                          primary_keys=[])

        self.assertRaises(
            dynamodb_exceptions.CreatingTableWithInvalidParams,
            self._create_table,
            table_name,
            primary_keys=[dynamodb_consts.property_schema(
                'Key2', dynamodb_consts.PrimaryKeyTypes.hash_type.value)]
        )

    def test_delete_table(self):

        # delete non existing table
        origin_logger = self._dynamodb_wrapper._logger
        self._dynamodb_wrapper._logger = unittest.mock.MagicMock()
        self._dynamodb_wrapper.delete_table(str(uuid.uuid1()))
        self._dynamodb_wrapper._logger.called_with(
            dynamodb_test_consts.SKIP_TABLE_DELETION_ERROR_MESSAGE)
        self._dynamodb_wrapper._logger = origin_logger

        # test successful delete table
        table_name = self._create_table_and_verify_its_existness()
        self._dynamodb_wrapper.delete_table(table_name)
        self.assertNotIn(table_name, self._dynamodb_wrapper.list_tables())

    def test_get_batch(self):

        # get from non existing table
        get_requests = dynamodb_consts.batch_get_config(
            str(uuid.uuid1()), dynamodb_test_consts.PRIMARY_KEY_NAME, ['a', 'b'])
        self.assertRaises(dynamodb_exceptions.BatchGetException,
                          self._dynamodb_wrapper.batch_get,
                          get_requests)

        # get non existing key from existing table
        table_name = self._create_table_and_verify_its_existness()
        get_requests = dynamodb_consts.batch_get_config(table_name,
                                                        dynamodb_test_consts.PRIMARY_KEY_NAME,
                                                        [str(uuid.uuid1())])
        self.assertEqual(len(self._get_response_content(get_requests)), 0)

        # get an existing key
        self._dynamodb_wrapper.batch_put(
            table_name, dynamodb_test_consts.VALID_ITEMS_TO_PUT)
        items_to_get = list(
            dynamodb_test_consts.VALID_ITEMS_TO_PUT[0].values())
        items_to_get.append(str(uuid.uuid1()))

        get_requests = dynamodb_consts.batch_get_config(
            table_name, dynamodb_test_consts.PRIMARY_KEY_NAME, items_to_get)
        get_output = self._get_response_content(get_requests)[0]
        self.assertEqual(get_output[dynamodb_test_consts.PRIMARY_KEY_NAME],
                         dynamodb_test_consts.VALID_ITEMS_TO_PUT[0][dynamodb_test_consts.PRIMARY_KEY_NAME])

    def test_delete_batch(self):
        keys_to_delete = dynamodb_test_consts.VALID_ITEMS_TO_PUT
        self.assertRaises(dynamodb_exceptions.BatchDeleteException,
                          self._dynamodb_wrapper.batch_delete,
                          str(uuid.uuid1()),
                          keys_to_delete)

        table_name = self._create_table_and_verify_its_existness()

        # Test no existing keys from existing table
        self._dynamodb_wrapper.batch_delete(table_name, keys_to_delete)

        # Test deletion existing keys from existing tables
        items_to_put = copy.copy(dynamodb_test_consts.VALID_ITEMS_TO_PUT)
        items_to_put[0]['b'] = 'bb'
        self._dynamodb_wrapper.batch_put(table_name, items_to_put)
        get_requests = dynamodb_consts.batch_get_config(table_name,
                                                        dynamodb_test_consts.PRIMARY_KEY_NAME,
                                                        items_to_put[0].values())

        pre_deletion_get_response_content = self._get_response_content(
            get_requests)
        for response in pre_deletion_get_response_content:
            self.assertIn(response, items_to_put)

        # test deletion with partly existing keys
        partly_existing_keys = []
        for key_value in [str(uuid.uuid1()), items_to_put[0][dynamodb_test_consts.PRIMARY_KEY_NAME]]:
            partly_existing_keys.append(
                {dynamodb_test_consts.PRIMARY_KEY_NAME: key_value})

        self._dynamodb_wrapper.batch_delete(table_name, partly_existing_keys)
        self.assertEqual(0, len(self._get_response_content(get_requests)))

    def test_put_batch(self):
        items_to_put = copy.copy(dynamodb_test_consts.VALID_ITEMS_TO_PUT)
        new_key_name = 'b'
        items_to_put[0][new_key_name] = 'bb'

        # put in non exists table
        self.assertRaises(dynamodb_exceptions.BatchPutException,
                          self._dynamodb_wrapper.batch_put,
                          str(uuid.uuid1()),
                          items_to_put)

        table_name = self._create_table_and_verify_its_existness()
        self._dynamodb_wrapper.batch_put(table_name, items_to_put)
        get_requests = dynamodb_consts.batch_get_config(table_name,
                                                        dynamodb_test_consts.PRIMARY_KEY_NAME,
                                                        [dynamodb_test_consts.DEFAULT_PRIMARY_KEY_VALUE, new_key_name])
        output = self._get_response_content(get_requests)
        self.assertEqual(len(output), 1)
        original_b_value = output[0][new_key_name]

        # Test update an existing key
        items_to_put[0][new_key_name] = 'bla'
        self._dynamodb_wrapper.batch_put(table_name, items_to_put)
        updated_b_value = self._get_response_content(get_requests)[
            0][new_key_name]
        self.assertNotEqual(original_b_value, updated_b_value)
        self.assertEqual(updated_b_value, items_to_put[0][new_key_name])

        self.assertRaises(dynamodb_exceptions.BatchPutException,
                          self._dynamodb_wrapper.batch_put,
                          table_name,
                          dynamodb_test_consts.ITEMS_TO_PUT_WITHOUT_PRIMARY_KEY)

        self.assertRaises(dynamodb_exceptions.BatchPutException,
                          self._dynamodb_wrapper.batch_put,
                          table_name,
                          dynamodb_test_consts.ITEMS_TO_PUT_WITH_MISMATCH_PRIMARY_KEY_VALUE)

    def test_put_item(self):
        primary_key_name = 'Y'
        number_value = 10
        item_to_put = {
            dynamodb_test_consts.PRIMARY_KEY_NAME: primary_key_name,
            'num': number_value
        }

        # Put item without condition
        self.assertRaises(dynamodb_exceptions.PutItemException,
                          self._dynamodb_wrapper.put_item,
                          str(uuid.uuid1()),
                          item_to_put)

        # Put item without condition
        table_name = self._create_table_and_verify_its_existness()
        self._dynamodb_wrapper.put_item(table_name, item_to_put)

        get_requests = dynamodb_consts.batch_get_config(table_name,
                                                        dynamodb_test_consts.PRIMARY_KEY_NAME,
                                                        [primary_key_name])
        self.assertDictEqual(self._get_response_content(
            get_requests)[0], item_to_put)

        self._dynamodb_wrapper.put_item(table_name,
                                        item_to_put,
                                        condition=dynamodb_conditions.Condition.is_equal('num', number_value))
        self.assertDictEqual(self._get_response_content(
            get_requests)[0], item_to_put)

        self.assertRaises(dynamodb_exceptions.PutItemException,
                          self._dynamodb_wrapper.put_item,
                          table_name,
                          item_to_put,
                          dynamodb_conditions.Condition.is_equal('num', number_value * 12))

    @classmethod
    def tearDownClass(cls):
        for table_name in cls._table_list:
            try:
                cls._dynamodb_wrapper.delete_table(table_name)

            except (dynamodb_exceptions.WaiterException,
                    dynamodb_exceptions.TableDeletionException) as exc:
                cls._logger.warn('Failed to delete table',
                                 table_name=table_name, exc=exc)

        cls._dynamodb_wrapper = None


if __name__ == "__main__":
    unittest.main()
