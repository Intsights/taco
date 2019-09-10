# Welcome to Taco!
![Taco](https://github.com/Intsights/taco/raw/master/Taco-logo.png)
### TL;DR

Taco is an open-source library that will help you navigate the AWS maze. You would be able to build a state of the art AWS based platform without the complexity that tends to accompany processes like this. On top of that, Taco contains CloudFormation detailed and yet simplistic templates for AWS based CI/CD process that, at the time of writing, you won't find this kind of templates anywhere else.

### **What is in my Taco?**
*  **Pythonic wrappers to essential AWS services** and pythonic modules that implement high-level logic like cloud RefCounter and Mutex.
* **CI/CD instructions** - Taco reveals to you how to build a CI/CD processes using AWS products by sharing detailed CloudFomation templates of CodeBuild, IAM roles, and CodePipeline.

### Requirements:
-   Python 3.6.7
-   [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
-   [Botocore pythonic package](https://pypi.org/project/botocore/)
-   [Boto3 python package](https://pypi.org/project/boto3/)

### Installation:
```
 pip install IntsightsTaco
 ```

### *Why Should You Choose Taco? BECAUSE IT IS SIMPLE!*
**Do you want to create new SQS and send there a message? No problem!**

```python
sqs = sqs_wrapper.SQSWrapper(aws_access_key=aws_access_key,
                             aws_secret_key=aws_secret_key,
                             region_name=region_name)
sqs_creation_config = sqs_configs.SQSCreationConfig(queue_name,
                                                    enable_dead_letter_queue=True,
                                                    force_clean_queue=False,
                                                    visibility_timeout_seconds=60)
sqs.create_queue(sqs_creation_config)
sqs.send_message(queue_name=queue_name, data=message_body, delay_seconds=delay_seconds)
```
**WAIT! THERE IS MORE!**
Taco’s pythonic wrappers require exactly the same **4 parameters for initialization** - Few code lines and you have access to 4th most common AWS services:
```python
# ---- Logger ----
logger = taco.logger.logger.get_logger(name='initialize_wrappers_samples')

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
```

***We know your jaw just dropped, we can wait you will pick her up :)**


### Look beyond what you see - Documentation and More Details:

In case you want to dig a little dipper (with or without your Taco) to have a better understanding, we highly recommend you to:
* Examine our test files and samples - These files are the place to get to know this project details.
* Read the following blog posts (Don't worry, they do have TL; DR):
	* [Taco’s pythonic Wrappers](https://www.youtube.com/watch?v=EsYPry-9ukk) - You will understand how magnificent this open-source aws pythonic wrappers. They are like the high-level wrappers boto3 never had. Moreover, you will find logic implementations using Taco’s wrappers like
	* [Taco’s CI/CD instruction](https://www.youtube.com/watch?v=EsYPry-9ukk) - Do you use AWS services and wish to set up a catting edge CI/CD processe using CloudFomation, CodeBuild and CodePipeline ? Just read this post. Although it is a long post, we spare no details.



*So Long, and Thanks for All the Fish.*
