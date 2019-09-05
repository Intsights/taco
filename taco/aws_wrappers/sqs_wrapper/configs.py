import taco.aws_wrappers.sqs_wrapper.consts as sqs_consts


class SQSCreationConfig(object):

    def __init__(self,
                 queue_name,
                 enable_dead_letter_queue=True,
                 force_clean_queue=False,
                 visibility_timeout_seconds=sqs_consts.DefaultQueueConfig.visibility_timeout_seconds.value,
                 delay_rate_seconds=sqs_consts.DefaultQueueConfig.delay_rate_seconds.value,
                 retention_period_seconds=sqs_consts.DefaultQueueConfig.retention_period_seconds.value,
                 max_receive_count=sqs_consts.DefaultQueueConfig.max_receive_count.value):
        self.queue_name = queue_name
        self.enable_dead_letter_queue = enable_dead_letter_queue
        self.force_clean_queue = force_clean_queue
        self.visibility_timeout_seconds = visibility_timeout_seconds
        self.delay_rate_seconds = delay_rate_seconds
        self.retention_period_seconds = retention_period_seconds
        self.max_receive_count = max_receive_count

    @property
    def dlq_name(self):
        return sqs_consts.DefaultQueueConfig.dead_letter_queue_name_format.value.format(self.queue_name)

    @property
    def requested_data(self):
        return {
            'QueueName': sqs_consts.DefaultQueueConfig.queue_name_format.value.format(self.queue_name),
            'Attributes': {
                'DelaySeconds': str(self.delay_rate_seconds),
                'MessageRetentionPeriod': str(self.retention_period_seconds),
                'VisibilityTimeout': str(self.visibility_timeout_seconds)
            }
        }
