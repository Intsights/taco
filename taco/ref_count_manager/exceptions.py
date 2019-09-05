import taco.common.exceptions


class RefCounterException(taco.common.exceptions.DataDictException):
    pass


class CounterNotFound(RefCounterException):
    def __init__(self, table_name, primary_key, routing_id):
        super().__init__('Counter not found',
                         data_dict={
                             'table_name': table_name,
                             'primary_key': primary_key,
                             'routing_id': routing_id
                         })
