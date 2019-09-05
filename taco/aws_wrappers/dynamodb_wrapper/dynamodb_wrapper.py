import botocore.exceptions

import taco.common.logger_based_object

import taco.boto3.boto_config as boto_config
import taco.boto3.boto3_helpers as boto3_helpers

from . import exceptions as dynamodb_exceptions
from . import consts as dynamodb_consts


class DynamoDBWrapper(taco.common.logger_based_object.LoggerBasedObject):

    def __init__(self,
                 logger=None,
                 region_name=dynamodb_consts.DEFAULT_REGION,
                 waiter_config=dynamodb_consts.TABLE_WAIT_CONFIG,
                 aws_access_key=None,
                 aws_secret_key=None,
                 auto_scaler=None):
        super().__init__(logger=logger)
        self._waiter_config = waiter_config
        self._default_region_name = region_name
        self._auto_scaler = auto_scaler
        self._dynamodb_client, self._dynamodb_resource = \
            boto3_helpers.get_client_resource(aws_access_key,
                                              aws_secret_key,
                                              boto_config.Boto3Resources.dynamodb.value,
                                              self._default_region_name)

    def _execute_batch_write_request(self, table_name, request_list, requests_type, request_key_arg_name):
        formatted_requests = []
        for single_request in request_list:
            formatted_item_properties = {}
            for property_name, property_value in single_request.items():
                formatted_item_properties[property_name] = property_value

            formatted_requests.append({
                requests_type: {
                    request_key_arg_name: formatted_item_properties
                }
            })

        return self._dynamodb_resource.batch_write_item(RequestItems={table_name: formatted_requests})

    def _create_formatted_attributes(self, attribute_list, attribute_arg_name):
        formatted_attributes = []
        for attribute in attribute_list:
            formatted_attributes.append({
                'AttributeName': attribute.name,
                attribute_arg_name: attribute.property_key_type
            })
        return formatted_attributes

    def _wait_for_table(self, table_name, waiter_kind):
        try:
            waiter = self._dynamodb_client.get_waiter(waiter_kind)
            waiter.wait(TableName=table_name, WaiterConfig=self._waiter_config)

        except botocore.exceptions.WaiterError as exc:
            self._logger.log_and_raise(dynamodb_exceptions.WaiterException,
                                       waiter_kind=waiter_kind,
                                       table_name=table_name,
                                       exc=exc)

    # --- Table ---
    def list_tables(self):
        try:
            return self._dynamodb_client.list_tables()['TableNames']

        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(dynamodb_exceptions.DynamoDBWrapperException,
                                       message='List tables failed',
                                       exc=exc)

    def delete_table(self, table_name):
        try:
            self.get_table(table_name).delete()
            self._wait_for_table(
                table_name, dynamodb_consts.TableWaiters.missing.value)

        except botocore.exceptions.ClientError as exc:
            if boto3_helpers.is_exception_type(exc, dynamodb_consts.CustomClientErrors.resource_missing.value):
                self._logger.debug('Table does not exists, skip deletion')
                return
            if boto3_helpers.is_exception_type(exc, dynamodb_consts.CustomClientErrors.resource_being_used.value):
                if boto3_helpers.is_in_exception_message(exc, dynamodb_consts.ErrorMessages.table_being_created.value):
                    self._logger.debug(
                        'Table is being created, waiting for it to exist to delete it')
                    self._wait_for_table(
                        table_name, dynamodb_consts.TableWaiters.exist.value)
                    self.get_table(table_name).delete()
                    self._wait_for_table(
                        table_name, dynamodb_consts.TableWaiters.missing.value)
                elif boto3_helpers.is_in_exception_message(exc, dynamodb_consts.ErrorMessages.table_being_deleted.value):
                    self._logger.debug(
                        'Table is already being deleted, skip deletion')
                return

    # TODO: make sure all functions use this method
    def get_table(self, table_name):
        return self._dynamodb_resource.Table(table_name)

    def create_table(self, table_creation_config, auto_scale=False):
        table_creation_with_invalid_params_kwargs = table_creation_config.__dict__
        table_creation_with_invalid_params_kwargs['exception_type'] = dynamodb_exceptions.CreatingTableWithInvalidParams

        try:
            self._dynamodb_resource.create_table(
                TableName=table_creation_config.table_name,
                KeySchema=self._create_formatted_attributes(
                    table_creation_config.primary_keys, 'KeyType'),
                ProvisionedThroughput=dynamodb_consts.PROVISIONED_THROUGHPUT,
                AttributeDefinitions=self._create_formatted_attributes(
                    table_creation_config.attribute_definitions, 'AttributeType')
            )

        except self._dynamodb_client.exceptions.ResourceInUseException as exc:
            for error_message in dynamodb_consts.IgnoredErrors.table_creation.value:
                if error_message in exc.args[0]:
                    self._logger.debug(
                        'Table already exists', table_name=table_creation_config.table_name)
                    return

        except botocore.exceptions.ParamValidationError as exc:
            table_creation_with_invalid_params_kwargs['exc'] = exc
            self._logger.log_and_raise(
                **table_creation_with_invalid_params_kwargs)

        except botocore.exceptions.ClientError as exc:
            if boto3_helpers.is_exception_type(exc, dynamodb_consts.CustomClientErrors.validation_exception.value):
                table_creation_with_invalid_params_kwargs['exc'] = exc
                self._logger.log_and_raise(
                    **table_creation_with_invalid_params_kwargs)

        except Exception as exc:
            self._logger.log_and_raise(dynamodb_exceptions.TableCreationException,
                                       table_name=table_creation_config.table_name,
                                       exc=exc)

        self._wait_for_table(table_creation_config.table_name,
                             dynamodb_consts.TableWaiters.exist.value)

        if auto_scale:
            for scalable_dimension, scalable_dimension_config in table_creation_config.scalable_dimension.items():
                self._auto_scaler.auto_scale(boto_config.Boto3Resources.dynamodb.value,
                                              table_creation_config.resource_id,
                                              scalable_dimension,
                                              scalable_dimension_config.min_dimension_unit,
                                              scalable_dimension_config.max_dimension_unit,
                                              scalable_dimension_config.metric_specification)

    # --- Items ---
    def batch_get(self, get_requests):
        formatted_key_list = []
        for key_value in get_requests.keys_value:
            formatted_key_list.append({get_requests.key_name: key_value})

        formatted_get_requests = {
            get_requests.table_name: {
                'ConsistentRead': dynamodb_consts.BatchGetConfig.consistent_read.value,
                'Keys': formatted_key_list
            }
        }

        try:
            return self._dynamodb_resource.batch_get_item(
                RequestItems=formatted_get_requests,
                ReturnConsumedCapacity=dynamodb_consts.ReturnConsumedCapacity.zero.value,
            )

        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(dynamodb_exceptions.BatchGetException,
                                       table_name=get_requests.table_name,
                                       get_requests=get_requests,
                                       exc=exc)

    def batch_put(self, table_name, put_requests):
        try:
            return self._execute_batch_write_request(table_name,
                                                     put_requests,
                                                     dynamodb_consts.BatchRequest.put.value,
                                                     dynamodb_consts.WriteOpsItemKeyName.item_arg.value)
        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(dynamodb_exceptions.BatchPutException,
                                       put_requests=put_requests,
                                       table_name=table_name,
                                       exc=exc)

    def batch_delete(self, table_name, delete_requests):
        try:
            return self._execute_batch_write_request(table_name,
                                                     delete_requests,
                                                     dynamodb_consts.BatchRequest.delete.value,
                                                     dynamodb_consts.WriteOpsItemKeyName.key_arg.value)

        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(dynamodb_exceptions.BatchDeleteException,
                                       table_name=table_name,
                                       delete_requests=delete_requests,
                                       exc=exc)

    @property
    def max_batch_size(self):
        return dynamodb_consts.MAX_BATCH_SIZE

    def put_item(self, table_name, put_request, condition=None):
        """
        Condition format is documented here:
        https://boto3.amazonaws.com/v1/documentation/api/latest/_modules/boto3/dynamodb/conditions.html
        """
        try:
            table = self.get_table(table_name)
            if condition:
                return table.put_item(Item=put_request, ConditionExpression=condition)

            return table.put_item(Item=put_request)

        except botocore.exceptions.ClientError as exc:
            exception_params = {
                'put_request': put_request,
                'table_name': table_name,
                'exc': exc
            }
            if condition is not None:
                exception_params['condition'] = condition.get_expression()

            self._logger.log_and_raise(
                dynamodb_exceptions.PutItemException, **exception_params)

    # --- Tags ---
    def tag_table(self, table_name, **tags):
        # Change tags dict to the format tag_resource accepts
        formatted_tags = [
            {dynamodb_consts.TagsResponseKeys.key.value: key,
             dynamodb_consts.TagsResponseKeys.value.value: value} for key, value in iter(tags.items())
        ]

        try:
            table = self.get_table(table_name)
            self._dynamodb_client.tag_resource(
                ResourceArn=table.table_arn, Tags=formatted_tags)
        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(dynamodb_exceptions.TagTableException,
                                       table_name=table_name,
                                       tags=tags,
                                       exc=exc)

    def untag_table(self, table_name, *tag_keys):
        try:
            table = self.get_table(table_name)
            self._dynamodb_client.untag_resource(
                ResourceArn=table.table_arn, TagKeys=tag_keys)
        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(dynamodb_exceptions.UntagTableException,
                                       table_name=table_name,
                                       tag_keys=tag_keys,
                                       exc=exc)

    def list_table_tags(self, table_name):
        try:
            table = self.get_table(table_name)
            tags_response = self._dynamodb_client.list_tags_of_resource(
                ResourceArn=table.table_arn)
            formatted_tags = tags_response[dynamodb_consts.TagsResponseKeys.tags.value]

            return {
                tag[dynamodb_consts.TagsResponseKeys.key.value]: tag[dynamodb_consts.TagsResponseKeys.value.value]
                for tag in formatted_tags
            }
        except botocore.exceptions.ClientError as exc:
            self._logger.log_and_raise(dynamodb_exceptions.ListTableTagsException,
                                       table_name=table_name,
                                       exc=exc)
