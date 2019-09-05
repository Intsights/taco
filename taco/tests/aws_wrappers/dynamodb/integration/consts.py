import taco.aws_wrappers.dynamodb_wrapper.consts as dynamodb_consts
from taco.boto3.boto_config import Regions


DEFAULT_REGION = Regions.n_virginia.value
RESPONSE_KEY_NAME = 'Responses'
PRIMARY_KEY_NAME = 'KEY1'
ATTRIBUTE_DEFINITIONS = [
    dynamodb_consts.property_schema(PRIMARY_KEY_NAME, dynamodb_consts.AttributeTypes.string_type.value)
]
PRIMARY_KEYS = [dynamodb_consts.property_schema(PRIMARY_KEY_NAME, dynamodb_consts.PrimaryKeyTypes.hash_type.value)]

ITEMS_TO_PUT_WITHOUT_PRIMARY_KEY = [{'q': 'qqq'}]

ITEMS_TO_PUT_WITH_MISMATCH_PRIMARY_KEY_VALUE = [{PRIMARY_KEY_NAME: 12}]
DEFAULT_PRIMARY_KEY_VALUE = '123abc'
VALID_ITEMS_TO_PUT = [{PRIMARY_KEY_NAME: DEFAULT_PRIMARY_KEY_VALUE}]
TABLE_ALREADY_EXISTS_MESSAGE = 'Table already exists'
SKIP_TABLE_DELETION_ERROR_MESSAGE = 'Table does not exists, skip deletion'
