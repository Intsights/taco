from enum import Enum

RUNTIME_CONFIG_FILE_NAME = 'runtime_configs.json'  # Use env var to determine this in the future
NEO4J_RESOURCE_NAME = 'conclusion_db'
URLS_SEPARATOR = ','


class ConfigKey(Enum):
    sqs = 'SQS'
    s3 = 'S3'
    generic_data = 'GenericData'
