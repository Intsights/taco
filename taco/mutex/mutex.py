import uuid
import datetime
import pytz

import taco.common.logger_based_object
from taco.aws_wrappers.dynamodb_wrapper import condition as dynamodb_condition, exceptions as dynamodb_exceptions
from taco.mutex import consts as mutex_consts
from taco.mutex import exceptions as mutex_exceptions


class CloudMutex(taco.common.logger_based_object.LoggerBasedObject):

    def __init__(self,
                 lock_name,
                 dynamodb_wrapper,
                 holder=None,
                 ttl=mutex_consts.DEFAULT_TTL,
                 table_name=mutex_consts.DEFAULT_MUTEX_TABLE_NAME,
                 logger=None):
        super().__init__(logger=logger)

        # Lock name is the mutex id while holder represents ths locker id.
        # Both are required in order to allow easy multiple lock by same holder

        self._lock_name = lock_name
        self._dynamodb_wrapper = dynamodb_wrapper
        self._ttl = ttl
        self._table_name = table_name if table_name is not None else mutex_consts.DEFAULT_MUTEX_TABLE_NAME
        self._holder = holder if holder else str(uuid.uuid4())

    def _get_now_epoch_time(self, tz=pytz.utc):
        return int(datetime.datetime.now(tz=tz).timestamp())

    def _get_put_request(self, expiration_time):
        return {
            mutex_consts.MutexDynamoConfig.lock.value: self._lock_name,
            mutex_consts.MutexDynamoConfig.holder.value: self._holder,
            mutex_consts.MutexDynamoConfig.ttl.value: expiration_time
        }

    def _prune_expired_lock(self):
        time_now = self._get_now_epoch_time()
        self._logger.debug('Prune expired lock',
                           table_name=self._table_name,
                           lock_name=self._lock_name,
                           caler=self._holder,
                           time_now=time_now)

        try:
            self._dynamodb_wrapper.put_item(
                self._table_name,
                self._get_put_request(0),
                dynamodb_condition.Condition.number_lower_than(mutex_consts.MutexDynamoConfig.ttl.value, time_now) |
                dynamodb_condition.Condition.not_exists(mutex_consts.MutexDynamoConfig.lock.value))

        except (dynamodb_exceptions.PutItemConditionException, dynamodb_exceptions.PutItemException):
            self._logger.log_and_raise(
                mutex_exceptions.MutexPruneException, self._lock_name, self._holder, str(self._ttl))

    def _lock_imp(self):
        expiration_time = self._get_now_epoch_time() + self._ttl
        self._logger.debug('Try Lock', lock_name=self._lock_name,
                           caler=self._holder, expiration_time=expiration_time)

        try:
            self._dynamodb_wrapper.put_item(
                self._table_name,
                self._get_put_request(expiration_time),
                dynamodb_condition.Condition.is_equal(mutex_consts.MutexDynamoConfig.holder.value, mutex_consts.NO_HOLDER_DATA) |
                dynamodb_condition.Condition.is_equal(mutex_consts.MutexDynamoConfig.holder.value, self._holder) |
                dynamodb_condition.Condition.not_exists(mutex_consts.MutexDynamoConfig.lock.value))

        except (dynamodb_exceptions.PutItemConditionException, dynamodb_exceptions.PutItemException):
            self._logger.log_and_raise(
                mutex_exceptions.MutexLockFailedException, self._lock_name, self._holder, str(self._ttl)
            )

    def _release_imp(self):
        """
        Release procedure is done by writing __no_holder__ and 0 ttl to the mutex dynamo object BUT
        Only in case of [OR] (1) No current holder (dummy operation)
                             (2) No dynamo representation for the mutex (first time creation)
                             (3) Release request is done from actual mutex holder
        """

        self._logger.debug(
            'Release Lock', lock_name=self._lock_name, caler=self._holder)

        try:
            self._dynamodb_wrapper.put_item(
                self._table_name,
                {
                    mutex_consts.MutexDynamoConfig.lock.value: self._lock_name,
                    mutex_consts.MutexDynamoConfig.holder.value: mutex_consts.NO_HOLDER_DATA,
                    mutex_consts.MutexDynamoConfig.ttl.value: 0,
                },
                dynamodb_condition.Condition.is_equal(mutex_consts.MutexDynamoConfig.holder.value, mutex_consts.NO_HOLDER_DATA) |
                dynamodb_condition.Condition.is_equal(mutex_consts.MutexDynamoConfig.holder.value, self._holder) |
                dynamodb_condition.Condition.not_exists(mutex_consts.MutexDynamoConfig.lock.value))

        except (dynamodb_exceptions.PutItemConditionException, dynamodb_exceptions.PutItemException):
            self._logger.log_and_raise(
                mutex_exceptions.MutexReleaseFailedException, self._lock_name, self._holder, str(self._ttl))

    def lock(self):
        try:
            self._prune_expired_lock()
        except mutex_exceptions.MutexPruneException:
            # Prune is a "best effort" opperation
            pass

        self._lock_imp()
        self._logger.debug('Mutex locked', lock_name=self._lock_name, holder=self._holder)

    def release(self):
        self._release_imp()
        self._logger.debug('Mutex released', lock_name=self._lock_name, holder=self._holder)

    # TODO: implement spinlcok

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
