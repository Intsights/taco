class DataDictException(Exception):

    def __init__(self, message, data_dict=None, exc=None):
        self._message = message
        if data_dict is None:
            data_dict = {}

        formatted_data_dict = {}
        for key, value in data_dict.items():
            formatted_data_dict[str(key)] = str(value)

        if exc is not None:
            formatted_data_dict['exc'] = str(exc)
        self._formatted_data_dict = formatted_data_dict

        formatted_message = '{0}: {1}'.format(self._message,
                                              str(formatted_data_dict).replace(': ', '=').replace('\'', '')[1:-1])
        super().__init__(formatted_message)
