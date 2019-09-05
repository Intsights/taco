import json
from enum import Enum


class TestConfigKeys(Enum):
    sqs = 'sqs_key'
    generic_data = 'generic_data_resource'
    s3 = 's3_bucket_key'


class TestConfigValues(Enum):
    s3 = 'bucket_name'
    sqs = 'sqs_resource'
    generic_data = 'abc'


run_time_config = json.dumps({
    "SQS": {
        TestConfigKeys.sqs.value: TestConfigValues.sqs.value,
    },
    "S3": {
        TestConfigKeys.s3.value: TestConfigValues.s3.value,
    },
    "GenericData": {
        TestConfigKeys.generic_data.value:  TestConfigValues.generic_data.value,
    }
})
