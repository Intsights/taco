import json

from taco.boto3.boto_config import Regions


DEFAULT_REGION = Regions.n_virginia.value
BASE_QUEUE_FORMAT = r'test-queue-{uid}'

DEFAULT_SQS_VISIBILITY_TIMEOUT = 30
MESSAGE_DELAY = 15

VISIBILITY_TIMEOUT_SECONDS = 2

RAW_DATA_TEST = 'hello ' * 100 + 'world'
JSON_DATA_TEST = json.dumps(RAW_DATA_TEST)

DELAY_FOR_MESSAGE_READ = 5
