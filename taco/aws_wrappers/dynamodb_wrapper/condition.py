import boto3.dynamodb.conditions as boto_conditions


class Condition(object):

    @staticmethod
    def is_equal(attribute_name, tester_data):
        return boto_conditions.Attr(attribute_name).eq(tester_data)

    @staticmethod
    def not_exists(attribute_name):
        return boto_conditions.Attr(attribute_name).not_exists()

    @staticmethod
    def number_lower_than(attribute_name, tester_data):
        return boto_conditions.Attr(attribute_name).lt(tester_data)
