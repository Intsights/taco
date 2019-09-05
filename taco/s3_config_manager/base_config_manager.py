import json

import taco.common.logger_based_object
from . import exceptions as config_exceptions


class BaseConfigManager(taco.common.logger_based_object.LoggerBasedObject):

    def __init__(self,
                 s3_wrapper,
                 bucket_name,
                 config_file_path,
                 logger=None):

        super().__init__(logger=logger)

        try:
            raw_config = s3_wrapper.get_file_data(bucket_name, config_file_path)
            self._logger.debug('Runtime config read', bucket_name=bucket_name, config_file_path=config_file_path,
                            size=len(raw_config))

            self._config = json.loads(raw_config)

        except Exception as exc:
            self._logger.log_and_raise(config_exceptions.CorruptedConfigFile, bucket_name=bucket_name,
                                       config_file=config_file_path, exc=exc)

    def _get_value(self, key_name):
        value = self._config.get(key_name)
        if not value:
            self._logger.log_and_raise(config_exceptions.MissingConfig, key_name)
        return value
