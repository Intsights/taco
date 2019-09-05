from taco.s3_config_manager.base_config_manager import BaseConfigManager


class ConfigurableConstsManager(BaseConfigManager):

    def __init__(self,
                 s3_wrapper,
                 consts_file_path,
                 bucket_name,
                 logger=None):
        super().__init__(s3_wrapper=s3_wrapper,
                         bucket_name=bucket_name,
                         config_file_path=consts_file_path,
                         logger=logger)

    # ------------- Getters -------------
    def get_const(self, const_name):
        return self._get_value(const_name)
