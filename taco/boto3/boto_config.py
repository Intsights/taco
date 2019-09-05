import logging
from enum import Enum


class DefaultBotoLogConfig(Enum):
    logger_name_format = 'boto3.resources{0}'
    default_log_level = logging.CRITICAL


class BotoResponseKeys(Enum):
    error = 'Error'
    code = 'Code'
    message = 'Message'


class Regions(Enum):
    ohio = 'us-east-2'
    n_virginia = 'us-east-1'
    eu = 'eu-west-1'


class Boto3Resources(Enum):
    dynamodb = 'dynamodb'
    s3 = 's3'
    sqs = 'sqs'
    ssm = 'ssm'
    application_autoscaling = 'application-autoscaling'
    stepfunctions = 'stepfunctions'


class AWSEnvVarKeyNames(Enum):
    default_region = 'AWS_DEFAULT_REGION'
    default_log_level = 'RA_DEFAULT_LOGGER_LOG_LEVELS'
    boto3_default_log_level = 'RA_BOTO3_LOGGER_LOG_LEVELS'
    runtime_config_bucket = 'RUNTIME_CONFIG_BUCKET'


DEFAULT_REGION = Regions.n_virginia.value
DEFAULT_BATCH_SIZE = 10


DEFAULT_WAIT_CONFIG = {
    'Delay': 2,  # The amount of time in seconds to wait between attempts.
    'MaxAttempts': 10  # The maximum number of attempts to be made
}
