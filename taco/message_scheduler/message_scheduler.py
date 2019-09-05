import json
import datetime
from botocore.exceptions import ClientError

from taco.boto3.boto_config import Boto3Resources
from taco import aws_wrappers as boto3_helpers, common

from . import consts as scheduler_consts
from . import exceptions as scheduler_exceptions


class MessageScheduler(common.ra_object.RAObject):

    def __init__(self,
                 infrastructure_wrappers,
                 region_name=scheduler_consts.DEFAULT_REGION,
                 logger=None):
        super().__init__(logger=logger)
        self._runtime_config_manager = infrastructure_wrappers.runtime_config_manager
        self._default_region_name = region_name
        
        self._step_function_client, _ = boto3_helpers.get_client_resource(
            infrastructure_wrappers.ssm.aws_access_key,
            infrastructure_wrappers.ssm.aws_secret_key,
            Boto3Resources.stepfunctions.value,
            self._default_region_name,
            ignore_resource=True
        )

    def _generate_json_payload(self, dst_queue, interval_sec, data):
        return json.dumps({
            scheduler_consts.ExecutionConsts.dst_queue.value: dst_queue,
            scheduler_consts.ExecutionConsts.ttl.value: interval_sec,
            **data,
        })
    
    def schedule_message(self, description, dst_queue_key, interval_min, data, message_scheduler_step_func_arn):
        # NOTE: data param should be formatted using sqs.get_formatted_data
        interval_sec = interval_min * 60
        
        # 'arn:aws:states:us-east-1:743607508365:stateMachine:message-scheduler'
        dst_queue_value = self._runtime_config_manager.get_sqs_queue(dst_queue_key)

        payload = self._generate_json_payload(dst_queue_value, interval_sec, data)
        self._logger.debug('Generated payload for tasks scheduler', payload=payload)

        try:
            # NOTE: total len of name str shoould be < 80
            response = self._step_function_client.start_execution(
                stateMachineArn=message_scheduler_step_func_arn,
                name=scheduler_consts.TASK_NAME_FORMAT.format(
                    description=description,
                    time_stamp=datetime.datetime.now().strftime(scheduler_consts.TASK_TIMESTAMP_FORMAT)),
                input=payload)
        
            self._logger.info('Message scheduled for delivery', response=response)

        except ClientError as exc:
            if not boto3_helpers.is_exception_type(exc, scheduler_consts.SpecificClientErrors.already_exists.value):
                self._logger.log_and_raise(scheduler_exceptions.GeneralException, exc=exc)

            self._logger.debug('Message already scheduled', exc=exc)


