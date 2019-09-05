from enum import Enum


import taco.boto3.boto_config


DEFAULT_REGION = taco.boto3.boto_config.DEFAULT_REGION
MAX_GET_PARAM_RETIES = 4
GET_PARAM_WAIT_IN_SEC = 1

THROTTLING_EXCEPTION = 'ThrottlingException'


class SSMParamNames(Enum):
    aws_secret_key = 'secret-key'
    aws_access_key = 'access-key'


class ParameterKeyNames(Enum):
    parameter = 'Parameter'
    value = 'Value'

