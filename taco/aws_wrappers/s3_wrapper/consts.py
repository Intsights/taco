import botocore.config
from enum import Enum

import taco.boto3.boto_config as boto_config


WAIT_CONFIG = boto_config.DEFAULT_WAIT_CONFIG
DEFAULT_REGION = boto_config.Regions.ohio.value
DEFAULT_DATA_ENCODING = 'utf-8'
DEFAULT_RESOURCE_CONFIG = botocore.config.Config(

    # The maximum number of retry attempts that will be made on a single request
    retries={'max_attempts': 5}
)


class ContentType(Enum):
    default = r'binary/octet-stream'
    html = r'text/html'
    javascript = r'application/javascript'
    css = r'text/css'
    plain_text = r'text/plain'
    png = r'image/png'
    gif = r'image/gif'
    svg_xml = r'image/svg+xml'
    font_woff = r'application/font-woff'


class IgnoredErrors(Enum):
    bucket_deletion = ['NoSuchBucket']
    bucket_creation = ['BucketAlreadyOwnedByYou']  # BucketAlreadyExists exception means it exists in other account
    object_missing = ['404']


class MetadataDirective(Enum):
    replace = 'REPLACE'
    copy = 'COPY'


class Waiters(Enum):
    object_exists = 'object_exists'
