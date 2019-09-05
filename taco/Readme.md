
# Welcome to pythonic AWS wrappers with Taco!

### TL;DR:
Have you ever wished to create an anazing pythonic system that use AWS infrastructure but got lost in boto3 documentation? Taco is here to save the day! Taco contains **pythonic wrappers for aws most common services** like:
-   S3
-   SQS
-   DynamoDB
-   AutoScaler
-   SSM
    
### Why you should use Taco’ pythonic AWS wrappers?
It's true that boto3 exposes all AWS services in a pythonic high-level way but it does not really simplify:
-   Boto3 offers excessive documentation.
-   There are multiple ways to do the same thing: AWS pythonic library named boto3 offers 3 ways (wrappers to their RESTful APIs) to access your IaaS resources:
	-  Client - A low-level wrapper for aws platform that
    - Resource - higher-level, object-oriented API
	-  Session - stores configuration information  
      
In short, **boto3 is confusing ¯\_(ツ)_/¯**.

### Taco is here to save the day!
Taco really untangled boto3 library and also helps you to:

-   **Avoid reading the documentation repeatedly** whenever we wanted to use an AWS service - we avoided questions like “Should we use boto resource or client?” (as a rule of thumb, use higher abstraction possible for every operation)
-   **What do we say to code duplication? Not today** - We guess you send messages in more than one place in your code and we all want to catch exceptions, make sure that all messages were sent, etc.
    
-   **Make sure our infrastructure works as expected** - We tested our wrappers and use it in our production environment.
    
-   **Program faster** - you do not have to get to know the pure core of boto to use our wrapper - it is written in a human language.
    


### Do not believe us? See for yourself!
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

#### Here is another example, just for you!
```python
wrappers_kwargs = {  
  'aws_access_key': aws_access_key,  
  'aws_secret_key': aws_secret_key,  
  'region_name': region_name  
}

s3 = s3_wrapper.S3Wrapper(**wrappers_kwargs)

# S3 create bucket  
bucket_name = str(uuid.uuid1().hex)  
s3.create_bucket(bucket_name, region_name=Regions.ohio.value)  
  
# upload the data to s3  
file_path = 'hello_world'  
s3.upload_data_to_file(bucket_name=bucket_name, file_path=file_path, data=read_message.data)  
  
# update file metadata  
new_metadata = {'a': 'b'}  
s3.update_file_metadata(bucket_name=bucket_name, file_path=file_path, new_metadata=new_metadata)
```
  
  


**For more information, you read this [post](https://www.youtube.com/watch?v=wPSZp_rOXHg&list=RDaQZDyyIyQMA&index=4).**

### Remember, Do not re:invent the wheel, use Taco!
