import botocore.exceptions

import taco.common.logger_based_object

from taco.boto3.boto_config import Boto3Resources
import taco.boto3.boto3_helpers as boto3_helpers

from taco.aws_wrappers.auto_scaler_wrapper import exceptions as autoscaling_exceptions, \
    consts as autoscaling_consts


class AutoScalerWrapper(taco.common.logger_based_object.LoggerBasedObject):

    def __init__(self,
                 aws_access_key=None,
                 aws_secret_key=None,
                 logger=None,
                 region_name=autoscaling_consts.DEFAULT_REGION):
        super().__init__(logger=logger)
        self._default_region_name = region_name
        self._client, _ = boto3_helpers.get_client_resource(aws_access_key,
                                                            aws_secret_key,
                                                            Boto3Resources.application_autoscaling.value,
                                                            self._default_region_name,
                                                            ignore_resource=True)

    def _register_scalable_target(self, service_namespace, resource_id, scalable_dimension, min_capacity, max_capacity):
        try:
            self._client.register_scalable_target(ServiceNamespace=service_namespace,
                                                  ResourceId=resource_id,
                                                  ScalableDimension=scalable_dimension,
                                                  MinCapacity=min_capacity,
                                                  MaxCapacity=max_capacity)
        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(autoscaling_exceptions.TargetRegistrationException,
                                       service_namespace=service_namespace,
                                       resource_id=resource_id,
                                       exc=str(exc))

    def _put_scaling_policy(self, service_namespace, resource_id, scalable_dimension, policy_name, metric_specification):

        try:
            # Auto generate policy name
            self._client.put_scaling_policy(
                ServiceNamespace=service_namespace,
                ResourceId=resource_id,
                PolicyType=autoscaling_consts.ScalePolicies.target.value,
                PolicyName=policy_name,
                ScalableDimension=scalable_dimension,
                TargetTrackingScalingPolicyConfiguration={
                    **autoscaling_consts.COMMON_TARGET_TRACKING_SCALING_POLICY_CONFIGURATION,
                    **metric_specification
                }
            )

        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(autoscaling_exceptions.PutPolicyException,
                                       service_namespace=service_namespace,
                                       resource_id=resource_id,
                                       exc=str(exc))

    def auto_scale(self,
                   service_namespace,
                   resource_id,
                   scalable_dimension,
                   min_capacity,
                   max_capacity,
                   metric_specification,
                   policy_name=None):
        if policy_name is None:
            policy_name = autoscaling_consts.POLICY_TEMPLATE.format(
                service_namespace=service_namespace,
                resource_id=resource_id,
                scalable_dimension=scalable_dimension
            ).replace(':', '_')
        self._register_scalable_target(
            service_namespace, resource_id, scalable_dimension, min_capacity, max_capacity)
        self._put_scaling_policy(service_namespace, resource_id,
                                 scalable_dimension, policy_name, metric_specification)
