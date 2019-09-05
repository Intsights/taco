from enum import Enum


class MutexDynamoConfig(Enum):
    lock = 'name'
    ttl = 'ttl'
    holder = 'holder'


NO_HOLDER_DATA = '__empty__'
DEFAULT_TTL = 60
DEFAULT_MUTEX_TABLE_NAME = 'mutex'
