import os
import logging

import taco.logger.consts as logger_consts

LOGS_BASE_DIR_PATH = r'./Output/Logs/'


class KwargsLogger(object):

    def __init__(self, logger=None, log_level=logging.DEBUG):
        self._logger = logger
        self.set_level(log_level)

    def _format_message(self, message, **kwrags):
        if kwrags is None:
            kwrags = {}

        formatted_kwargs = []
        for key, value in kwrags.items():
            formatted_kwargs.append('{0}={1}'.format(str(key).replace('\'', ''), str(value).replace('\'', '')))
        return '{0}: {1}'.format(message, ', '.join(formatted_kwargs))

    def get_child(self, logger_name):
        child_logger = self._logger.getChild(logger_name)
        return KwargsLogger(logger=child_logger)

    def log_and_raise(self, exception_type, *exception_args, **exception_kwargs):
        exception_obj = exception_type(*exception_args, **exception_kwargs)
        self._logger.error(str(exception_obj))
        raise exception_obj

    def add_handler(self, handler):
        self._logger.addHandler(handler)

    def set_level(self, level):
        self._logger.setLevel(level)

    def error(self, msg, *args, **kwargs):
        format_message = self._format_message(msg, **kwargs)
        self._logger.error(format_message)

    def info(self, msg, *args, **kwargs):
        format_message = self._format_message(msg, **kwargs)
        self._logger.info(format_message)

    def debug(self, msg, *args, **kwargs):
        format_message = self._format_message(msg, **kwargs)
        self._logger.debug(format_message)

    def warn(self, msg, *args, **kwargs):
        format_message = self._format_message(msg, **kwargs)
        self._logger.warning(format_message)


def get_logger(name, add_file_handler=False, log_level=logger_consts.DEFAULT_LOG_LEVEL):
    logger = KwargsLogger(logging.Logger(name), log_level=log_level)
    formatter = logging.Formatter(
        '%(asctime)s-%(name)s-%(levelname)s %(filename)s-%(lineno)d %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.add_handler(ch)

    if add_file_handler:
        if not os.path.exists(LOGS_BASE_DIR_PATH):
            os.makedirs(LOGS_BASE_DIR_PATH)

        fh = logging.FileHandler(
            LOGS_BASE_DIR_PATH + '{name}.log'.format(name=name))
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.add_handler(fh)

    return logger
