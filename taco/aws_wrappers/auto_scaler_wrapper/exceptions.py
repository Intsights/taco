import taco.common.exceptions


class AutoScalerWrapperException(taco.common.exceptions.DataDictException):
    pass


# --- Table ---
class TargetRegistrationException(AutoScalerWrapperException):
    def __init__(self, service_namespace, resource_id, exc):
        super().__init__('Failed to register auto scaler',
                         data_dict={
                             'resource_id': resource_id,
                             'service_namespace': service_namespace
                         }, exc=exc)


class PutPolicyException(AutoScalerWrapperException):
    def __init__(self, service_namespace, resource_id, exc):
        super().__init__('Failed to register auto scaler',
                         data_dict={
                             'resource_id': resource_id,
                             'service_namespace': service_namespace
                         }, exc=exc)
