import boto3

import taco.boto3.boto_config as aws_wrappers_boto_config


def get_client_resource(aws_access_key, aws_secret_key, service_name, region_name, config=None, ignore_resource=False):
    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region_name,
    )
    boto_kwargs = {
        'service_name': service_name,
        'region_name': region_name,
        'config': config
    }

    resource = None
    if not ignore_resource:
        resource = session.resource(**boto_kwargs)

    return (session.client(**boto_kwargs), resource)


def set_boto3_log_level(logger_name, log_level):
    boto3.set_stream_logger(aws_wrappers_boto_config.DefaultBotoLogConfig.logger_name_format.value.format(logger_name), log_level)


def is_exception_type(exc, exception_types):
    received_exception_type =\
        exc.response[aws_wrappers_boto_config.BotoResponseKeys.error.value][aws_wrappers_boto_config.BotoResponseKeys.code.value]
    return received_exception_type in exception_types


def is_in_exception_message(exc, message_segment):
    exc_message =\
        exc.response[aws_wrappers_boto_config.BotoResponseKeys.error.value][aws_wrappers_boto_config.BotoResponseKeys.message.value]
    return message_segment in exc_message
