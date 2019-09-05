from enum import Enum

from taco import common

DEFAULT_REGION = common.consts.aws.DEFAULT_REGION

TASK_NAME_FORMAT = r'{description}-{unique_id}-{time_stamp}'
TASK_TIMESTAMP_FORMAT = r'%Y%m%d%-H'


class ExecutionConsts(Enum):
    ttl = 'timer_seconds'
    dst_queue = 'queue_url'


class SpecificClientErrors(Enum):
    already_exists = 'ExecutionAlreadyExists'
