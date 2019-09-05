import taco.common.exceptions


class SQSWrapperException(taco.common.exceptions.DataDictException):
    pass


class SQSClientException(SQSWrapperException):

    def __init__(self, message='SQS client error', data_dict=None, exc=None):
        super().__init__(message, data_dict=data_dict, exc=exc)


class SendMessageException(SQSWrapperException):
    def __init__(self, data, queue_name, exc=None):
        data_dict = {
            'data': data,
            'queue_name': queue_name
        }
        super().__init__('Failed to send message', data_dict=data_dict, exc=exc)


class ListQueuesClientException(SQSClientException):

    def __init__(self, exc=None):
        super().__init__('SQS list queues client error', exc=exc)


class CreateQueuesClientException(SQSClientException):

    def __init__(self, queue_creation_config, exc=None):
        super().__init__('SQS create queue client error',
                         data_dict={'queue_creation_config': queue_creation_config},
                         exc=exc)


class GetQueueClientException(SQSClientException):

    def __init__(self, queue_name, exc=None):
        super().__init__('SQS get queue by name client error', data_dict={'queue_name': queue_name}, exc=exc)


class ClearQueueClientException(SQSClientException):

    def __init__(self, queue_name, exc=None):
        super().__init__('SQS clear queue client error', data_dict={'queue_name': queue_name}, exc=exc)


class DeleteQueueClientException(SQSClientException):

    def __init__(self, queue_name, exc=None):
        super().__init__('SQS delete queue client error', data_dict={'queue_name': queue_name}, exc=exc)


class SendMessageClientException(SQSClientException):

    def __init__(self, queue_name, data_messages, exc=None):
        data_dict = {
            'queue_name': queue_name,
            'data_messages': data_messages
        }
        super().__init__('SQS send messages client error', data_dict=data_dict, exc=exc)


class ReadMessageClientException(SQSClientException):

    def __init__(self, queue_name, exc=None):
        super().__init__('SQS read messages client error', data_dict={'queue_name': queue_name}, exc=exc)


class DeleteMessageClientException(SQSClientException):

    def __init__(self, exc=None):
        super().__init__('SQS delete messages client error', exc=exc)


class SQSNonExistingQueueException(SQSWrapperException):

    def __init__(self, queue_name, exc=None):
        super().__init__('None existing queue name',  data_dict={'queue_name': queue_name}, exc=exc)


class SQSInvalidParamsException(SQSWrapperException):

    def __init__(self, params, exc=None):
        super().__init__('AWS invalid param exception',
                         data_dict={'params': params}, exc=exc)


class SQSCreateExistingQueueParamsErrorException(SQSWrapperException):

    def __init__(self, params, exc=None):
        super().__init__('A queue already exists with the same name and a different value for an attribute',
                         data_dict={'params': params}, exc=exc)


class SQSMessageWrapperException(SQSWrapperException):
    pass


class SQSDecodingException(SQSMessageWrapperException):

    def __init__(self, exc=None):
        super().__init__('SQS Message decoding exception', exc=exc)
