import taco.logger.logger

from taco.boto3.boto_config import Regions
import taco.aws_wrappers.ssm_wrapper.ssm_wrapper as ssm_wrapper
import taco.aws_wrappers.sqs_wrapper.sqs_wrapper as sqs_wrapper
import taco.aws_wrappers.s3_wrapper.s3_wrapper as s3_wrapper
import taco.aws_wrappers.dynamodb_wrapper.dynamodb_wrapper as dynamodb_wrapper
import taco.aws_wrappers.auto_scaler_wrapper.auto_scaler_wrapper as auto_scaler_wrapper

# This module demonstrate how to initialize our wrappers. For more details take a look at our test files.


def initialize_wrappers(aws_access_key=None, aws_secret_key=None, region_name=Regions.n_virginia.value):
    # ---- Logger ----
    logger = taco.logger.logger.get_logger(name='initialize_wrappers_samples')

    # ---- AWS Services ----

    # SSM
    ssm = ssm_wrapper.SSMWrapper(logger=logger)
    if aws_secret_key is None:
        aws_secret_key = ssm.aws_secret_key

    if aws_access_key is None:
        aws_access_key = ssm.aws_access_key

    wrappers_default_kwargs = {
        'logger': logger,
        'aws_access_key': aws_access_key,
        'aws_secret_key': aws_secret_key,
        'region_name': region_name
    }

    # SQS
    sqs = sqs_wrapper.SQSWrapper(**wrappers_default_kwargs)

    # S3 wrapper
    s3 = s3_wrapper.S3Wrapper(**wrappers_default_kwargs)

    # Auto Scaler
    auto_scaler = auto_scaler_wrapper.AutoScalerWrapper(**wrappers_default_kwargs)

    # DynamoDB - without auto scaler
    dynamodb = dynamodb_wrapper.DynamoDBWrapper(**wrappers_default_kwargs)
    dynamodb_with_auto_scaler = dynamodb_wrapper.DynamoDBWrapper(auto_scaler=auto_scaler, **wrappers_default_kwargs)


def main():
    initialize_wrappers()


if __name__ == '__main__':
    main()
