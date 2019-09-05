from taco.aws_wrappers.dynamodb_wrapper import table_creation_config as table_creation_config, \
    consts as dynamodb_consts

import taco.ref_count_manager.consts as ref_count_manager_consts


class RefCountTableCreation(table_creation_config.TableCreationConfig):

    def __init__(self, table_name=ref_count_manager_consts.REF_COUNT_DEFAULT_TABLE_NAME):
        super().__init__(table_name,

                         # primary key
                         [
                             dynamodb_consts.property_schema(
                                 ref_count_manager_consts.RefCountTableConfig.routing_id.value,
                                 dynamodb_consts.PrimaryKeyTypes.hash_type.value
                             ),
                         ],

                         # Attributes definitions
                         [
                             dynamodb_consts.property_schema(
                                 ref_count_manager_consts.RefCountTableConfig.routing_id.value,
                                 dynamodb_consts.AttributeTypes.string_type.value
                             ),
                         ]
                         )
