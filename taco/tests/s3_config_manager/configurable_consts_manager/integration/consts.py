from enum import Enum
import json


class TestConsts(Enum):
    my_const = 'your_const'


class TestConfigValues(Enum):
    runtime_config_bucket_name = 'test-runtime-config-bucket'
    consts_file_path = 'configurable_consts_test.json'
    corrupted_json_file_path = 'corrupted_json_file.json'


config = json.dumps({
    TestConsts.my_const.name: TestConsts.my_const.value
})
