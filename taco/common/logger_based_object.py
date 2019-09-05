import taco.logger.logger


class LoggerBasedObject(object):

    def __init__(self, logger=None):
        logger_name = self.__class__.__name__
        if logger is None:
            self._logger = taco.logger.logger.get_logger(logger_name)

        else:
            self._logger = logger.get_child(logger_name)
