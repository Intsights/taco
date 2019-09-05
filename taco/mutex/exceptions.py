import taco.common.exceptions


class MutexException(taco.common.exceptions.DataDictException):
    pass


class MutexLockFailedException(MutexException):
    def __init__(self, lock_name, holder, ttl, exc=None):
        data_dict = {
            'lock_name': lock_name,
            'holder': holder,
            'ttl': ttl,
        }
        super().__init__('Mutex lock exception', data_dict, exc=exc)


class MutexReleaseFailedException(MutexException):
    def __init__(self, lock_name, holder, ttl, exc=None):
        data_dict = {
            'lock_name': lock_name,
            'holder': holder,
            'ttl': ttl,
        }
        super().__init__('Mutex release exception', data_dict, exc=exc)


class MutexPruneException(MutexException):
    def __init__(self, lock_name, holder, ttl, exc=None):
        data_dict = {
            'lock_name': lock_name,
            'holder': holder,
            'ttl': ttl,
        }
        super().__init__('Mutex prune exception', data_dict, exc=exc)
