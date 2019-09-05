# NOTE: this test is sanity but VERY EXPENSIVE and therefore should not run periodically

import unittest
import uuid

import taco.logger.logger

from taco.boto3.boto_config import Boto3Resources
import taco.aws_wrappers.dynamodb_wrapper.dynamodb_wrapper as dynamodb_wrapper
import taco.aws_wrappers.auto_scaler_wrapper.auto_scaler_wrapper as auto_scaler_wrapper
import taco.aws_wrappers.auto_scaler_wrapper.exceptions as auto_scaler_exceptions
import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper
from taco.tests.aws_wrappers.auto_scaler_wrapper.integration import consts as test_consts

import taco.mutex.mutex_table_creation_config as mutex_table_creation_config


class TestAutoScaler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = taco.logger.logger.get_logger('TestAutoScaler')
        cls._ssm_wrapper = ssm_wrapper.SSMWrapper(logger=cls._logger)
        aws_access_key = cls._ssm_wrapper.aws_access_key
        aws_secret_key = cls._ssm_wrapper.aws_secret_key
        cls._dynamodb_wrapper = dynamodb_wrapper.DynamoDBWrapper(logger=cls._logger,
                                                                 aws_access_key=aws_access_key,
                                                                 aws_secret_key=aws_secret_key,
                                                                 region_name=test_consts.DEFAULT_REGION)
        cls._auto_scaler_wrapper = auto_scaler_wrapper.AutoScalerWrapper(logger=cls._logger,
                                                                         region_name=test_consts.DEFAULT_REGION,
                                                                         aws_access_key=aws_access_key,
                                                                         aws_secret_key=aws_secret_key)

        cls._table_name = str(uuid.uuid1())
        cls._resource_id = 'table/{table_name}'.format(
            table_name=cls._table_name)
        cls._dynamodb_wrapper.create_table(
            mutex_table_creation_config.MutexTableCreation(
                table_name=cls._table_name)
        )

    @property
    def register_args(self):
        return {
            'service_namespace': Boto3Resources.dynamodb.value,
            'resource_id': str(uuid.uuid1()),
            **test_consts.DEAFULT_Scaler_ARGS
        }

    def test_auto_scale(self):
        auto_scale_args = self.register_args
        auto_scale_args['resource_id'] = self._resource_id
        auto_scale_args['policy_name'] = str(uuid.uuid1())
        auto_scale_args['metric_specification'] = {
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'DynamoDBReadCapacityUtilization'
            }
        }
        self._auto_scaler_wrapper.auto_scale(**auto_scale_args)

    def test_put_scaling_policy(self):
        self.assertRaises(auto_scaler_exceptions.PutPolicyException,
                          self._auto_scaler_wrapper._put_scaling_policy,
                          str(uuid.uuid1()),
                          str(uuid.uuid1()),
                          str(uuid.uuid1()),
                          str(uuid.uuid1()),
                          {})

    def test_register_scalable_target(self):

        register_args = self.register_args
        self.assertRaises(auto_scaler_exceptions.TargetRegistrationException,
                          self._auto_scaler_wrapper._register_scalable_target,
                          **register_args)

        register_args['resource_id'] = self._resource_id
        for _ in range(2):
            self._auto_scaler_wrapper._register_scalable_target(
                **register_args)

        register_args['service_namespace'] = str(uuid.uuid1())
        self.assertRaises(auto_scaler_exceptions.TargetRegistrationException,
                          self._auto_scaler_wrapper._register_scalable_target,
                          **register_args)

        register_args['service_namespace'] = Boto3Resources.dynamodb.value
        register_args['scalable_dimension'] = str(uuid.uuid1())

        self.assertRaises(auto_scaler_exceptions.TargetRegistrationException,
                          self._auto_scaler_wrapper._register_scalable_target,
                          **register_args)

    @classmethod
    def tearDownClass(cls):
        try:
            cls._dynamodb_wrapper.delete_table(cls._table_name)

        except Exception as exc:
            cls._logger.warn('Failed to delete table',
                             table_name=cls._table_name, exc=exc)

        cls._dynamodb_wrapper = None


if __name__ == "__main__":
    unittest.main()
