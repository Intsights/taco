from taco.boto3.boto_config import Regions


DEFAULT_REGION = Regions.n_virginia.value
PUT_SCALLING_POLICY_ERROR_MESSAGE = 'PutScalingPolicy operation: 2 validation errors detected'

DEAFULT_Scaler_ARGS = {
    'scalable_dimension': 'dynamodb:table:ReadCapacityUnits',
    'min_capacity': 50,
    'max_capacity': 100,
}
