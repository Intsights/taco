from taco.boto3.boto_config import Regions


DEFAULT_REGION = Regions.ohio.value
BUCKET_ALREADY_EXISTS_ERROR_MESSGAE = 'Bucket already exist'
BUCKET_MISSING_ERROR_MESSAGE = 'The specified bucket does not exist'
FILE_MISSING_ERROR_MESSAGE = 'The specified key does not exist'
NOT_FOUND_ERROR_MESSAGE = 'Not Found'

FILE_DATA = 'son of man'
ALTERNATIVE_FILE_DATA = 'Hakuna matata'
DEFAULT_METADATA = {
    'mufasa': 'and so we are all connected in the great circle of life',
    'scar': 'im surrounded by idiots'
}

ALTERNATIVE_METADATA = {
    'jerry_maguire': 'you had me at hello',
}

All_METADATA = {**ALTERNATIVE_METADATA, **DEFAULT_METADATA}
