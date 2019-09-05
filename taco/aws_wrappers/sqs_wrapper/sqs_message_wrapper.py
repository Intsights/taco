import json

import taco.common.logger_based_object


class SQSMessageWrapper(taco.common.logger_based_object.LoggerBasedObject):

    def __init__(self, message_id, receipt_handle, queue_url, data_body='""', logger=None):
        super().__init__(logger=logger)
        self._message_id = message_id
        self._receipt_handle = receipt_handle
        self._queue_url = queue_url

        try:
            self._data = json.loads(data_body)

        except json.decoder.JSONDecodeError as exc:
            # self._logger.log_and_raise(sqs_exceptions.SQSDecodingException, exc=exc)
            self._data = data_body

    def __str__(self):
        return 'Message ID: {0}, Receipt Handle: {1}, Data keys: {2}'.format(
            self._message_id, self._receipt_handle, str(self._data.keys()))

    @property
    def message_id(self):
        return self._message_id

    @property
    def data(self):
        return self._data

    @property
    def receipt_handle(self):
        return self._receipt_handle

    @property
    def queue_url(self):
        return self._queue_url
