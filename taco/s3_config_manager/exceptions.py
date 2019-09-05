import taco.common.exceptions


class RuntimeConfigManagerException(taco.common.exceptions.DataDictException):
    pass


class MissingConfig(RuntimeConfigManagerException):
    def __init__(self, key_name):
        data_dict = {'key_name': key_name}
        super().__init__('Failed to locate key', data_dict=data_dict)


class CorruptedConfigFile(RuntimeConfigManagerException):
    def __init__(self, bucket_name, config_file, exc=None):
        data_dict = {'config_file': config_file,
                     'bucket_name': bucket_name}
        super().__init__('Missing or invalid config file in S3', data_dict=data_dict, exc=exc)
