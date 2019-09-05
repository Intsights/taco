import json
from botocore.exceptions import ClientError, ParamValidationError

import taco.boto3.boto_config as boto_config
import taco.boto3.boto3_helpers as boto3_helpers

import taco.common.logger_based_object

from taco.aws_wrappers.sqs_wrapper import consts as sqs_consts
from taco.aws_wrappers.sqs_wrapper import exceptions as sqs_exceptions
from taco.aws_wrappers.sqs_wrapper import sqs_message_wrapper as sqs_message_wrapper


class SQSWrapper(taco.common.logger_based_object.LoggerBasedObject):

    def __init__(self, region_name=sqs_consts.DEFAULT_REGION, aws_access_key=None, aws_secret_key=None, logger=None):
        super().__init__(logger=logger)
        self._default_region_name = region_name
        self._sqs_client, self._sqs_resource = boto3_helpers.get_client_resource(aws_access_key,
                                                                                 aws_secret_key,
                                                                                 boto_config.Boto3Resources.sqs.value,
                                                                                 self._default_region_name)

    def list_queues(self):
        try:
            return self._sqs_client.list_queues().get(sqs_consts.QUEUES_URL_TAG, [])

        except ClientError as exc:
            self._logger.log_and_raise(sqs_exceptions.ListQueuesClientException, exc=exc)

    def create_queue(self, queue_creation_config):
        """
        We will will not support FIFO queues in order to scale out this solution
        """
        try:
            if queue_creation_config.enable_dead_letter_queue:
                dead_letter_queue = self._sqs_resource.create_queue(QueueName=queue_creation_config.dlq_name)
                self._logger.info('Create Dead Letter SQS Queue', name=queue_creation_config.dlq_name)

                redrive_policy = {}
                redrive_policy['maxReceiveCount'] = queue_creation_config.max_receive_count
                redrive_policy['deadLetterTargetArn'] = dead_letter_queue.attributes['QueueArn']

            if queue_creation_config.force_clean_queue and self.is_queue_exists(queue_creation_config.queue_name):
                self.clear_queue(queue_creation_config.queue_name)

            else:
                self._logger.info('Create SQS Queue', requested_data=queue_creation_config.requested_data)
                queue = self._sqs_resource.create_queue(**queue_creation_config.requested_data)
                self._logger.info('New SQS Queue', url=queue.url, attributes=queue.attributes)

            if queue_creation_config.enable_dead_letter_queue:
                self._logger.info("Set DLQ for SQS queue", attributes=redrive_policy)
                queue.set_attributes(
                    Attributes={'RedrivePolicy': json.dumps(redrive_policy)}
                )

        except ParamValidationError as exc:
            self._logger.log_and_raise(
                sqs_exceptions.SQSInvalidParamsException, params=queue_creation_config.requested_data, exc=exc)

        except ClientError as exc:
            if boto3_helpers.is_exception_type(exc, sqs_consts.SpecificClientErrors.existing_queue.value):
                self._logger.log_and_raise(
                    sqs_exceptions.SQSCreateExistingQueueParamsErrorException,
                    params=queue_creation_config.requested_data,
                    exc=exc)

            self._logger.log_and_raise(sqs_exceptions.CreateQueuesClientException,
                                       queue_creation_config=queue_creation_config,
                                       exc=exc)

    def get_queue_by_name(self, queue_name):
        try:
            self._logger.info('Find queue', name=queue_name)
            return self._sqs_resource.get_queue_by_name(
                QueueName=sqs_consts.DefaultQueueConfig.queue_name_format.value.format(queue_name),
            )

        except ClientError as exc:
            if boto3_helpers.is_exception_type(exc, sqs_consts.IgnoredErrors.non_existing_queue.value):
                self._logger.log_and_raise(sqs_exceptions.SQSNonExistingQueueException, queue_name, exc)

            self._logger.log_and_raise(sqs_exceptions.GetQueueClientException, queue_name=queue_name, exc=exc)

    def is_queue_exists(self, queue_name):
        try:
            self.get_queue_by_name(queue_name)
            return True

        except sqs_exceptions.SQSWrapperException:
            return False

    def clear_queue(self, queue_name):
        try:
            self._logger.info('Purge queue', queue=queue_name)
            queue = self.get_queue_by_name(queue_name)
            result = queue.purge()
            self._logger.info('Queue purge progress began', result=result)

        except ClientError as exc:
            if boto3_helpers.is_exception_type(exc, sqs_consts.IgnoredErrors.purge_queue_in_progress.value):
                self._logger.info('Client exception will be ignored',
                                  exception_type=sqs_consts.IgnoredErrors.purge_queue_in_progress.value)
                return

            self._logger.log_and_raise(sqs_exceptions.ClearQueueClientException, queue_name=queue_name, exc=exc)

    def delete_queue(self, queue_name, is_dlq=False):
        """
        Note (from AWS official documentation):
        "When you delete a queue, you must wait at least 60 seconds before creating a queue with the same name."
        """
        formatted_queue_name = sqs_consts.DefaultQueueConfig.dead_letter_queue_name_format.value.format(queue_name) \
            if is_dlq else sqs_consts.DefaultQueueConfig.queue_name_format.value.format(queue_name)

        self._logger.info('Delete queue', queue=formatted_queue_name)

        try:
            queue = self.get_queue_by_name(formatted_queue_name)
            result = queue.delete()
            self._logger.info('Queue deleted', queue=formatted_queue_name, result=str(result))

        except sqs_exceptions.SQSNonExistingQueueException:
            self._logger.info('Queue did not exist', queue=formatted_queue_name)

        except ClientError as exc:
            if boto3_helpers.is_exception_type(exc, sqs_consts.IgnoredErrors.non_existent_queue.value):
                self._logger.info('Client exception will be ignored',
                                  exception_type=sqs_consts.IgnoredErrors.non_existent_queue.value)
                return

            self._logger.log_and_raise(sqs_exceptions.DeleteQueueClientException, exc=exc)

    def _create_request_data(self, data, delay_seconds=None, message_id=None):
        requested_data = {
            'MessageBody': data,
        }
        if message_id is not None:
            requested_data['Id'] = message_id

        if delay_seconds is not None:
            requested_data['DelaySeconds'] = delay_seconds

        return requested_data

    def send_message(self, queue_name, data, delay_seconds=None):
        """
        Note: message data shoud be of json type
        """
        requested_data = self._create_request_data(data, delay_seconds)
        self._logger.debug('Send message', data=requested_data)

        queue = self.get_queue_by_name(queue_name)
        try:
            result = queue.send_message(**requested_data)
            self._logger.debug('Send message result', result=str(result))

        except ClientError as exc:
            self._logger.log_and_raise(sqs_exceptions.SendMessageClientException,
                                       queue_name=queue_name,
                                       data=data,
                                       exc=exc)

    def send_message_batch(self, queue_name, data_list, delay_seconds=None):
        current_butch_message_index = 0
        queue_url = self._sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']
        self._logger.debug('Start Sending batch', current_butch_message_index=current_butch_message_index)
        while current_butch_message_index < len(data_list):
            data_messages = []
            for message_id, data in enumerate(data_list[current_butch_message_index: current_butch_message_index+sqs_consts.BATCH_SIZE]):
                data_messages.append(self._create_request_data(data, delay_seconds, message_id=str(message_id)))

            self._logger.debug('Sending batch', current_butch_message_index=current_butch_message_index)
            try:
                result = self._sqs_client.send_message_batch(QueueUrl=queue_url, Entries=data_messages)

            except ClientError as exc:
                self._logger.log_and_raise(sqs_exceptions.SendMessageClientException,
                                           queue_name=queue_name,
                                           data_messages=data_messages,
                                           exc=exc)

            self._logger.debug('Send message result', result=str(result), current_butch_message_index=current_butch_message_index)
            if len(result[sqs_consts.BATCH_SUCCESSFUL_RESPONSE_KEY]) != len(data_messages):
                self._logger.log_and_raise(sqs_exceptions.SendMessageClientException,
                                           queue_name=queue_name,
                                           data_messages=data_messages,
                                           exc=exc)
            current_butch_message_index += sqs_consts.BATCH_SIZE

        self._logger.debug('Send all batch', current_butch_message_index=current_butch_message_index)

    def read_message(self, queue_name, delete_after_receive=True):
        queue = self.get_queue_by_name(queue_name)

        try:
            message = queue.receive_messages(**sqs_consts.RECIEVE_MESSAGE_CONSTS)

            if not message:
                return

            message = message[0]
            self._logger.debug('Received message')

            # Logically we want to overcome messages with invalid data (not json) so
            # we receive this message, delete it from the queue (regerdless client's willingt) but forward it for
            # processing only upon valid data

            try:
                sqs_message = sqs_message_wrapper.SQSMessageWrapper(message.message_id,
                                                                    message.receipt_handle,
                                                                    queue.url,
                                                                    message.body)

            except sqs_exceptions.SQSMessageWrapperException:
                self._logger.warn('Failed to decode message data. Deleting the message from the queue and ignore it')
                sqs_message = sqs_message_wrapper.SQSMessageWrapper(message.message_id,
                                                                    message.receipt_handle,
                                                                    queue.url)
                self.delete_messages([sqs_message])
                return

            if delete_after_receive:
                self.delete_messages([sqs_message])

            return sqs_message

        except ClientError as exc:
            self._logger.log_and_raise(sqs_exceptions.ReadMessageClientException, queue_name=queue_name, exc=exc)

    def read_messages(self, queue_name, delete_after_receive=True, messages_limit=1):
        all_messages = {}

        while not messages_limit or len(all_messages) < messages_limit:
            try:
                message = self.read_message(queue_name, delete_after_receive)

                # Note: this is redudnacy check sice MessageVisibilityTimeout should prevent situation of receiving
                # the same message to frequently
                if not message or message.message_id in all_messages.keys():
                    break

                all_messages[message.message_id] = message

            except sqs_exceptions.SQSClientException as exc:
                self._logger.debug(str(exc))
                break

        return list(all_messages.values())

    def delete_messages(self, sqs_messages):
        try:
            for sqs_message in sqs_messages:
                message = self._sqs_resource.Message(
                    sqs_message.queue_url, sqs_message.receipt_handle)
                message.delete()

        except ClientError as exc:
            self._logger.log_and_raise(sqs_exceptions.DeleteMessageClientException, exc=exc)
