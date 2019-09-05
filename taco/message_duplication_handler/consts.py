import datetime
from enum import Enum, auto

import taco.aws_wrappers.dynamodb_wrapper.consts as dynamodb_consts


class LambdaTriggerTypes(Enum):
    gateway_api = auto()
    sqs = auto()
    s3 = auto()


LAMBDA_ID_FORMAT = '{function_name}-{function_version}-{aws_request_id}'

SCHEMA_PRIMARY_KEY_NAME = 'LambdaID'

ATTRIBUTE_DEFINITIONS = [
    dynamodb_consts.property_schema(SCHEMA_PRIMARY_KEY_NAME, dynamodb_consts.AttributeTypes.string_type.value)
]

PRIMARY_KEYS = [
    dynamodb_consts.property_schema(SCHEMA_PRIMARY_KEY_NAME, dynamodb_consts.PrimaryKeyTypes.hash_type.value)
]

# Timeout before reprocessing a request for a specific id; set to lambda execution time limit
REPROCESS_TIMEOUT = datetime.timedelta(minutes=15).seconds
