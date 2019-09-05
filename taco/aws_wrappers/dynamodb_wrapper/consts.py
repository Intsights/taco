from collections import namedtuple
from enum import Enum

import taco.boto3.boto_config


DEFAULT_REGION = taco.boto3.boto_config.DEFAULT_REGION
DIMENSION_TEMPLATE = 'dynamodb:table:{0}'


class CapacitiesArgs(Enum):
    read = 'ReadCapacityUnits'
    write = 'WriteCapacityUnits'


READ_DIMENSION = DIMENSION_TEMPLATE.format(CapacitiesArgs.read.value)
WRITE_DIMENSION = DIMENSION_TEMPLATE.format(CapacitiesArgs.write.value)


class DimensionUnit(Enum):
    min = 500
    max = 1500


READ_METRIC_SPECIFICATION = {
    'PredefinedMetricSpecification': {
        'PredefinedMetricType': 'DynamoDBReadCapacityUtilization'
    }
}

WRITE_METRIC_SPECIFICATION = {
    'PredefinedMetricSpecification': {
        'PredefinedMetricType': 'DynamoDBWriteCapacityUtilization'
    }
}

scalable_dimension_config = namedtuple('ScalableDimensionConfig',
                                       'metric_specification min_dimension_unit max_dimension_unit')

SCALABLE_DIMENSION = {
    READ_DIMENSION: scalable_dimension_config(READ_METRIC_SPECIFICATION, DimensionUnit.min.value, DimensionUnit.max.value),
    WRITE_DIMENSION: scalable_dimension_config(WRITE_METRIC_SPECIFICATION, DimensionUnit.min.value, DimensionUnit.max.value),
}

batch_get_config = namedtuple('BatchGetConfig', 'table_name key_name keys_value')
property_schema = namedtuple('PropertySchema', 'name property_key_type')


# By defining your throughput capacity in advance, DynamoDB can reserve the necessary resources to meet the read
# and write activity your application requires, while ensuring consistent, low-latency performance
PROVISIONED_THROUGHPUT = {

    # The maximum number of strongly consistent reads consumed per second before DynamoDB returns a ThrottlingException
    # For example:
    #   One read capacity unit represents one strongly consistent read per second,
    #   or two eventually consistent reads per second, for an item up to 4 KB in size.
    CapacitiesArgs.read.value: 5,

    # The maximum number of writes per second before dynamodb returns a ThrottlingException.
    # For example:
    #   One write capacity unit represents one write per second for an item up to 1 KB in size.
    CapacitiesArgs.write.value: 5
}

TABLE_WAIT_CONFIG = {
    'Delay': 2,  # The amount of time in seconds to wait between attempts.
    'MaxAttempts': 100  # The maximum number of attempts to be made
}


class IgnoredErrors(Enum):
    table_creation = ['Table already exists', 'Table is being created']


class PrimaryKeyTypes(Enum):
    hash_type = 'HASH'  # partition key
    range_type = 'RANGE'  # sort key


class AttributeTypes(Enum):
    string_type = 'S'
    number_type = 'N'
    binary_type = 'B'


ATTRIBUTE_TYPE_TO_STRING_REPRESENTATION = {
    str: AttributeTypes.string_type.value,
    int: AttributeTypes.number_type.value,
}


# Determines the level of detail about provisioned throughput consumption that is returned in the response
class ReturnConsumedCapacity(Enum):
    zero = 'NONE'
    total = 'TOTAL'
    indexes = 'INDEXES'


class BatchRequest(Enum):
    put = 'PutRequest'
    delete = 'DeleteRequest'


class TableWaiters(Enum):
    exist = 'table_exists'
    missing = 'table_not_exists'


class WriteOpsItemKeyName(Enum):
    item_arg = 'Item'
    key_arg = 'Key'
    condition_arg = 'ConditionExpression'


class BatchGetConfig(Enum):
    consistent_read = True


class CustomClientErrors(Enum):
    condition_check_failed = ['ConditionalCheckFailedException']
    validation_exception = ['ValidationException']
    resource_missing = ['ResourceNotFoundException']
    resource_being_used = ['ResourceInUseException']


class ErrorMessages(Enum):
    table_being_created = 'Table is being created'
    table_being_deleted = 'Table is being deleted'


class TagsResponseKeys(Enum):
    tags = 'Tags'
    key = 'Key'
    value = 'Value'


MAX_BATCH_SIZE = 25
