import taco.common.logger_based_object
import taco.aws_wrappers.dynamodb_wrapper.consts as dynamodb_consts

from . import consts as ref_count_config_consts
from . import exceptions as ref_count_exceptions


class RefCountManager(taco.common.logger_based_object.LoggerBasedObject):

    def __init__(self,
                 dynamodb_wrapper,
                 table_name=ref_count_config_consts.REF_COUNT_DEFAULT_TABLE_NAME,
                 logger=None):
        super().__init__(logger=logger)
        self._table_name = table_name
        self._dynamodb_wrapper = dynamodb_wrapper

    # ------------- Helpers -------------
    def _update_count(self, unique_id, routing_type, update_attributes_values):
        formatted_id = self.get_formatted_routing_id(unique_id, routing_type)
        table = self._dynamodb_wrapper.get_table(self._table_name)
        return table.update_item(
            Key={
                ref_count_config_consts.RefCountTableConfig.routing_id.value: formatted_id,
            },
            **ref_count_config_consts.UPDATE_COUNTER_KWARGS,
            **update_attributes_values
        )

    def increament_count(self, unique_id, routing_type):
        return self._update_count(unique_id, routing_type, ref_count_config_consts.INCREAMENT_ATTRIBUTES_VALUES)

    def deccreament_count(self, unique_id, routing_type):
        return self._update_count(unique_id, routing_type, ref_count_config_consts.DECREMENT_ATTRIBUTES_VALUES)

    def get_formatted_routing_id(self, unique_id, routing_type):
        return ref_count_config_consts.ROUTING_ID_TEMPLATE.format(routing_type=routing_type,
                                                                  some_unique_id=unique_id)

    def get_current_ref_count(self, unique_id, routing_type):
        routing_id_value = self.get_formatted_routing_id(unique_id, routing_type)
        batch_get_config = dynamodb_consts.batch_get_config(self._table_name,
                                                            ref_count_config_consts.REF_COUNT_TABLE_PRIMARY_KEY_NAME,
                                                            [routing_id_value])
        for response in self._dynamodb_wrapper.batch_get(batch_get_config)['Responses'][self._table_name]:
            if response[ref_count_config_consts.REF_COUNT_TABLE_PRIMARY_KEY_NAME] == routing_id_value:
                return int(response[ref_count_config_consts.RefCountTableConfig.counter.value])

        self._logger.log_and_raise(ref_count_exceptions.CounterNotFound,
                                   table_name=self._table_name,
                                   primary_key=ref_count_config_consts.REF_COUNT_TABLE_PRIMARY_KEY_NAME,
                                   routing_id=routing_id_value)

    def remove_counter(self, unique_id, routing_type):
        routing_id_value = self.get_formatted_routing_id(unique_id, routing_type)
        self._logger.debug('Removing counter', table_name=self._table_name, routing_id=routing_id_value)
        delete_request = [{ref_count_config_consts.REF_COUNT_TABLE_PRIMARY_KEY_NAME: routing_id_value}]
        self._dynamodb_wrapper.batch_delete(self._table_name, delete_request)
        self._logger.debug('Removed counter', table_name=self._table_name, routing_id=routing_id_value)
