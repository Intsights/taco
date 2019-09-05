import taco.common.logger_based_object
import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper
import taco.aws_wrappers.dynamodb_wrapper.dynamodb_wrapper as dynamodb_wrapper_module

import taco.message_duplication_handler.consts as message_duplication_global_consts
from taco.message_duplication_handler import consts as message_duplication_aws_consts
import taco.mutex.exceptions as mutex_exceptions
from taco.mutex.mutex import CloudMutex


class message_duplication_handler(taco.common.logger_based_object.LoggerBasedObject):

    def __init__(self,
                 reprocess_timeout=message_duplication_global_consts.REPROCESS_TIMEOUT,
                 is_chalice_function=False,
                 logger=None,
                 mutex_table_name=None):
        super().__init__(logger=logger)
        self._reprocess_timeout = reprocess_timeout
        self._is_chalice_function = is_chalice_function
        self._mutex_table_name = mutex_table_name
        self._ssm_wrapper = ssm_wrapper.SSMWrapper(logger=self._logger)
        self._dynamodb_wrapper = dynamodb_wrapper_module.DynamoDBWrapper(logger=self._logger,
                                                                         aws_access_key=self._ssm_wrapper.aws_access_key,
                                                                         aws_secret_key=self._ssm_wrapper.aws_secret_key)

    def __call__(self, decorated_function):

        if self._is_chalice_function:
            function_name = decorated_function.func.__name__

        else:
            function_name = decorated_function.__name__

        def wrapped_decorated_function(event, context):

            lambda_id = message_duplication_aws_consts.LAMBDA_ID_FORMAT.format(
                function_name=context.function_name,
                function_version=context.function_version,
                aws_request_id=context.aws_request_id)

            log_args = {
                'lambda_id': lambda_id,
                'context': context,
                'ttl': self._reprocess_timeout,
                'function_name': function_name
            }
            self._logger.debug('executing wrapped function', **log_args)
            mutex = CloudMutex(lambda_id,
                               self._dynamodb_wrapper,
                               ttl=self._reprocess_timeout,
                               table_name=self._mutex_table_name)

            try:
                with mutex:

                    # If we are here -> good news, we managed to lock this mutex with lock name which is unique per
                    #     execution of lambdaI_name-lambda_generation-request_message
                    self._logger.debug('Execute lambda', **log_args)
                    return decorated_function(event, context)

            except mutex_exceptions.MutexLockFailedException as exc:
                self._logger.debug('Failed to lock lambda execution', exc=exc, **log_args)

        wrapped_decorated_function.__name__ = function_name
        return wrapped_decorated_function
