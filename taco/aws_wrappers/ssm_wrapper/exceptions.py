import taco.common.exceptions


class SSMGetParamException(taco.common.exceptions.DataDictException):
    def __init__(self, param_name):
        super().__init__('Failed to get param from ssm', data_dict={'param_name': param_name})
