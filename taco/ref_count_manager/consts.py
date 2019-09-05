from enum import Enum


class RefCountTableConfig(Enum):
    routing_id = 'routing_id'
    counter = 'routing_counter'


REF_COUNT_TABLE_PRIMARY_KEY_NAME = RefCountTableConfig.routing_id.value

ROUTING_ID_TEMPLATE = '{routing_type}:{some_unique_id}'
REF_COUNT_DEFAULT_TABLE_NAME = 'ref_count'
DEFAULT_START_COUNTER_VALUE = 0
UPDATE_COUNTER_KWARGS = {
    'UpdateExpression': 'SET {routing_counter_name} = if_not_exists({routing_counter_name} , :start) + :inc'.format(routing_counter_name=RefCountTableConfig.counter.value),
    'ReturnValues': 'UPDATED_NEW',
}

INCREAMENT_ATTRIBUTES_VALUES = {
    'ExpressionAttributeValues': {
        ':inc': 1,
        ':start': DEFAULT_START_COUNTER_VALUE,
    }
}

DECREMENT_ATTRIBUTES_VALUES = {
    'ExpressionAttributeValues': {
        ':inc': -1,
        ':start': DEFAULT_START_COUNTER_VALUE,
    }
}
