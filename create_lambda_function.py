# Adapted from source: https://aws.amazon.com/blogs/compute/using-aws-lambda-with-auto-scaling-lifecycle-hooks/

import boto3
import json

def DynamicallyCreateLambda():

    lambda_client = boto3.client('lambda')
	
    # First check if it already exists
    try:
        check_response = lambda_client.get_function(FunctionName='Test-Function')
        return
    except:
        print('No function exists. Will now be created.')
	
    # Connect
    iam_client = boto3.client('iam')
    sns_client = boto3.client('sns')

    # Create the SNS topic
    topic = sns_client.create_topic(Name='ead_design_ca_test1')
    topic_arn = topic['TopicArn'] 

    # Create the IAM policies
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [ {
	    "Sid": "",
	    "Effect": "Allow",
	    "Principal": {
	        "Service": "sns.amazonaws.com"
	    },
            "Action": "sts:AssumeRole"
        } ]
    }

    allow_topic_policy = {
        "Version": "2012-10-17",
	"Statement": [ {
	    "Effect": "Allow",
	    "Resource": "topic_arn",
	    "Action": [
	        "sns:Publish"
	    ]
	 } ]
    }

    # Create the role name and apply policies
    role = 'Test-Role'
    role_response = iam_client.create_role(
        RoleName = role,
	AssumeRolePolicyDocument = json.dumps(assume_role_policy)
    )

    myRole = role_response['Arn']

    trust_response = iam_client.put_role_policy(
        RoleName=myRole,
	PolicyName='myAllowTopicPolicy',
	PolicyDocument=json.dumps(allow_topic_policy)
    )

    # Create lambda	
    lambda_response = lambda_client.create_function(
        FunctionName='Test-Function',
        Runtime='python3.6'
        Role=myRole,
        Handler='lambda_handler.lambda_handler',
        Code={'ZipFile': 'lambda_handler.zip'  # this is a zip file containing my lambda_handler.py file
        }
    )

    myFunctionARN = lambda_response['FunctionArn']
    
    # Subscribe the Lambda function to the SNS topic
    sns_client.subscribe(
        TopicArn=topic_arn,
        Endpoint=myFunctionARN
    )

    # Grant permissions on the lambda function to the SNS topic
    lambda_permission_response = lambda_client.add_permission(
        FunctionName=myFunctionARN
	StatementId='1',
	Action='lambda:InvokeFunction',
	Principal='sns.amazonaws.com',
        SourceArn=topic_arn
    )

