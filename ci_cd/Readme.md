# CI/CD with Taco!

### TL; DR:
This folder contains CloudFormation templates that will help you form an **AWS base CI/CD cross accounts** (Each account represent a user):
-   CI/CD orchestrator
-   Tests account
-   Production account

### Requirements:
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)

### 5 services that are the core of Taco CI/CD process:
-  **CloudFomation** - A common, YAML like, language that details and provisions all the infrastructure resources in your AWS environment. This language, as opposed to the AWS console (GUI), gives you full control over AWS services.
-  **S3** - A storage service, used to store the tested and the deployable code.
-   **KMS** - A keys management service that creates and manages encryption keys that are used to encrypt the deployable code.
-   **CodeBuild** - A continuous integration service that runs tests, compiles source code and produces software packages that are ready for deployment.
-   **CodePipeline** - A fully managed continuous delivery service that helps you automate your release pipelines for fast and reliable


### A picture is worth a thousand words:
**![ci_cd](https://github.com/Intsights/taco/blob/master/ci_cd/ci_cd.png)**


### From where should I begin?
The CloudFormation templates are divided into 2:
-   **Simple**:  The templates in this folder are used to create a deployment process for simple AWS services One **Lambda without any Layers** that are activated via an SQS.
-   **Advanced**: This folder contains templates that demonstrate how to provision more tangled AWS infrastructure that includes a **Lambda with several Lamda layer and a Nested Stacks** that manage them all.
*Our recommendation is that whether you just started your journey with creating a functional CI/CD processes ontop AWS, or you are considering your self one level behind the “mother of dragons”, read this blog post <add a link>. Although it is a long post, we are sure it will clarify things and will help you learn more than a thing or two.


### How do you make it work?

This is how you build a simple CI/CD process that provisions Lamda deployment from our app_sample.
Note: Do not forget to fill in the params in our .yml files.



1.  Create **3 empty AWS accounts**, each will represent a different chain in our CI/CD process:
	* An account that will orchestrate the CI/CD process - the one that hosts CodePipeline and CodeBuild processes. During this guide, we will refer to this account as the CI/CD orchestrator.
	* An account that is an exact reflection of the production account.
	* An account that actual host your system and serves your customer, aka Production account.
2. Deploy **artifacts-kms.yml** in **CI/CD Orchestrator account**. This will create a **KMS** key and enable Test and Production account to access it.
    ```cli aws cloudformation deploy --stack-name KMSForCICDArtifacts --template-file artifacts-kms.yml --capabilities CAPABILITY_IAM```
3.  Create an **S3** Bucket. This Bucket will contain the **CI/CD artifacts**. Change this bucket **policies** as described at **artifacts_bucket_policies.json** and Do not forget to replace the following:
	* “YOURBUCKETNAME” with your actual artifacts bucket name
	* “TESTACCOUNTID” with your test account id
	* “PRODUCTIONACCOUNTID” with your production account id

4.  Deploy **iam-deployed-account.yml** on **both Test and Production accounts**. This will **enable the CI/CD Orchestrator account to access** these accounts via CodePipeline service and eploy resources via cloud formation services.
```aws cloudformation deploy --stack-name CICDPermissions --template-file iam-deployed-account.yml --capabilities CAPABILITY_NAMED_IAM```

5.  Deploy **code-build.yml** on **CI/CD Orchestrator account**. This will create a **CodeBuild Process**.
```aws cloudformation deploy --stack-name ExampleCodeBuild --template-file code-build.yml --capabilities CAPABILITY_IAM```

6.  Deploy **code-pipeline.yml** on **CI/CD Orchestrator account**. This will create the **CodePipeine process itself**.
```aws cloudformation deploy --stack-name <YOUR CODE PIPELINE STACK NAME> --template-file code-pipeline.yml --capabilities CAPABILITY_IAM```

