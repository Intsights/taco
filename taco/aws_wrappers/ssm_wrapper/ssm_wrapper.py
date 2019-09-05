import boto3
import time
import botocore

from taco.boto3.boto_config import Boto3Resources
from taco.aws_wrappers.ssm_wrapper import exceptions as ssm_exception, consts as ssm_consts
from taco.boto3 import boto3_helpers as boto3_helpers
import taco.common.logger_based_object


class SSMWrapper(taco.common.logger_based_object.LoggerBasedObject):

    def __init__(self, region_name=ssm_consts.DEFAULT_REGION, logger=None):
        super().__init__(logger=logger)
        self._default_region = region_name
        self._client = boto3.client(Boto3Resources.ssm.value, region_name=self._default_region)

    def _get_param_value(self, param_name, with_decryption=True):
        for _ in range(ssm_consts.MAX_GET_PARAM_RETIES):
            try:
                param = self._client.get_parameter(Name=param_name, WithDecryption=with_decryption)
                return param.get(ssm_consts.ParameterKeyNames.parameter.value, {}).get(ssm_consts.ParameterKeyNames.value.value, None)

            except botocore.exceptions.ClientError as exc:
                if not boto3_helpers.is_exception_type(exc, [ssm_consts.THROTTLING_EXCEPTION]):
                    raise exc

            self._logger.warn('Failed to get param, retrying in a sec', exc=str(exc))
            time.sleep(ssm_consts.GET_PARAM_WAIT_IN_SEC)

        self._logger.log_and_raise(ssm_exception.SSMGetParamException, param_name=param_name)

    @property
    def aws_access_key(self):
        return self._get_param_value(ssm_consts.SSMParamNames.aws_access_key.value)

    @property
    def aws_secret_key(self):
        return self._get_param_value(ssm_consts.SSMParamNames.aws_secret_key.value)
