from enum import Enum

import taco.boto3.boto_config


DEFAULT_REGION = taco.boto3.boto_config.DEFAULT_REGION

POLICY_TEMPLATE = 'auto_scale_policy_{resource_id}_{scalable_dimension}'
PERCENT_OF_USE_TO_AIM_FOR = 80.0
SCALE_OUT_COOLDOWN_IN_SECONDS = 60
SCALE_IN_COOLDOWN_IN_SECONDS = 60


COMMON_TARGET_TRACKING_SCALING_POLICY_CONFIGURATION = {
    'TargetValue': PERCENT_OF_USE_TO_AIM_FOR,
    'ScaleOutCooldown': SCALE_OUT_COOLDOWN_IN_SECONDS,
    'ScaleInCooldown': SCALE_IN_COOLDOWN_IN_SECONDS
}


class ScalePolicies(Enum):
    simple = 'SimpleScaling'
    step = 'StepScaling'
    target = 'TargetTrackingScaling'
