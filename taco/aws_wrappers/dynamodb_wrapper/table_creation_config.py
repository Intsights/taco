from . consts import SCALABLE_DIMENSION


class TableCreationConfig(object):

    def __init__(self, table_name, primary_keys, attribute_definitions):
        self.table_name = table_name
        self.primary_keys = primary_keys
        self.attribute_definitions = attribute_definitions

    @property
    def resource_id(self):
        return 'table/{table_name}'.format(table_name=self.table_name)

    @property
    def scalable_dimension(self):
        return SCALABLE_DIMENSION
