from taco.aws_wrappers.dynamodb_wrapper import table_creation_config as table_creation_config, \
    consts as dynamodb_consts
from taco.mutex.consts import MutexDynamoConfig, DEFAULT_MUTEX_TABLE_NAME


class MutexTableCreation(table_creation_config.TableCreationConfig):
    def __init__(self, table_name=DEFAULT_MUTEX_TABLE_NAME):
        super().__init__(table_name,

                         # primary key
                         [
                             dynamodb_consts.property_schema(MutexDynamoConfig.lock.value,
                                                             dynamodb_consts.PrimaryKeyTypes.hash_type.value)
                         ],

                         # Attributes definitions
                         [
                             dynamodb_consts.property_schema(MutexDynamoConfig.lock.value,
                                                             dynamodb_consts.AttributeTypes.string_type.value)
                         ]
                         )
