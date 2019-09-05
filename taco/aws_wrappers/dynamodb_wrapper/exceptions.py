import taco.common.exceptions


class DynamoDBWrapperException(taco.common.exceptions.DataDictException):
    pass


class WaiterException(DynamoDBWrapperException):
    def __init__(self, table_name, waiter_kind, exc=None):
        super().__init__('Table is invalid',
                         exc=exc,
                         data_dict={
                             'table_name': table_name,
                             'waiter_kind': waiter_kind
                         })


# --- Table ---
class TableDeletionException(DynamoDBWrapperException):
    def __init__(self, table_name, exc=None):
        super().__init__('Table deletion failed',
                         data_dict={'table_name': table_name}, exc=exc)


class TableCreationException(DynamoDBWrapperException):
    def __init__(self, table_name, exc=None):
        data_dict = {
            'table_name': table_name,
        }
        super().__init__('Table creation failed', data_dict=data_dict, exc=exc)


class CreatingTableWithInvalidParams(DynamoDBWrapperException):
    def __init__(self, table_name, primary_keys, attribute_definitions, exc=None):
        data_dict = {
            'table_name': table_name,
            'primary_keys': primary_keys,
            'attribute_definitions': attribute_definitions
        }
        super().__init__('Table creation prams are invalid', data_dict=data_dict, exc=exc)


# --- Batch ---
class BatchException(DynamoDBWrapperException):
    def __init__(self, message, table_name, batch_requests, exc=None):
        super().__init__(message, exc=exc, data_dict={
            'batch_requests': batch_requests,
            'table_name': table_name
        })


class BatchDeleteException(DynamoDBWrapperException):
    def __init__(self, table_name, delete_requests, exc=None):
        super().__init__('Delete batch request failed', data_dict={
            'table_name': table_name,
            'delete_requests': delete_requests,
        }, exc=exc)


class BatchGetException(DynamoDBWrapperException):
    def __init__(self, table_name, get_requests, exc=None):
        super().__init__('Batch get request failed', data_dict={
            'table_name': table_name,
            'get_requests': get_requests
        }, exc=exc)


class BatchPutException(DynamoDBWrapperException):
    def __init__(self, table_name, put_requests, exc=None):
        super().__init__('Batch put request failed', data_dict={
            'table_name': table_name,
            'put_requests': put_requests
        }, exc=exc)


class PutItemException(DynamoDBWrapperException):
    def __init__(self, table_name, put_request, condition=None, exc=None):
        super().__init__('Put item failed', data_dict={
            'table_name': table_name,
            'put_request': put_request,
            'condition': condition
        }, exc=exc)


class PutItemConditionException(DynamoDBWrapperException):
    def __init__(self, table_name, put_request, condition=None, exc=None):
        super().__init__('Put item condition failed', data_dict={
            'table_name': table_name,
            'put_request': put_request,
            'condition': condition
        }, exc=exc)


class TagTableException(DynamoDBWrapperException):
    def __init__(self, table_name, tags, exc=None):
        super().__init__('Tag table failed', data_dict={
            'table_name': table_name,
            'tags': tags
        }, exc=exc)


class UntagTableException(DynamoDBWrapperException):
    def __init__(self, table_name, tag_keys, exc=None):
        super().__init__('Untag table failed', data_dict={
            'table_name': table_name,
            'tag_keys': tag_keys
        }, exc=exc)


class ListTableTagsException(DynamoDBWrapperException):
    def __init__(self, table_name, tags, exc=None):
        super().__init__('List table tags failed', data_dict={
            'table_name': table_name
        }, exc=exc)
