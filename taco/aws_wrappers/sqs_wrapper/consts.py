from enum import Enum
import taco.boto3.boto_config

DEFAULT_REGION = taco.boto3.boto_config.DEFAULT_REGION
BATCH_SIZE = 10
BATCH_SUCCESSFUL_RESPONSE_KEY = 'Successful'


class RequestDataKeyId(Enum):

    additional_data = 'additional_data'


class AdditionalDataKeyNames(Enum):
    some_key = 'some_key'


class DefaultQueueConfig(Enum):
    queue_name_format = '{0}'
    dead_letter_queue_name_format = 'dead-letter-{0}'

    # Note: if this is bigger than 3 we fail to read for the 4th time at the dlq test
    max_receive_count = 3

    visibility_timeout_seconds = 30  # Limited by 12 hours
    delay_rate_seconds = 0
    retention_period_seconds = 345600  # 4 Days, limited by 14 days


class IgnoredErrors(Enum):
    non_existing_queue = ['AWS.SimpleQueueService.NonExistentQueue']
    queue_deleted_recently = ['AWS.SimpleQueueService.QueueDeletedRecently']
    purge_queue_in_progress = ['AWS.SimpleQueueService.PurgeQueueInProgress']


class SpecificClientErrors(Enum):
    existing_queue = ['QueueAlreadyExists']


QUEUES_URL_TAG = 'QueueUrls'

RECIEVE_MESSAGE_CONSTS = {
    'AttributeNames': ['All'],
    'MaxNumberOfMessages': 1,
}
