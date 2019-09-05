import taco.common.exceptions


class ScheduledMessageException(taco.common.exceptions.DataDictException):
    pass


class GeneralException(ScheduledMessageException):
    def __init__(self, exc=None):
        super().__init__('General StepFunction exception', exc=exc)
