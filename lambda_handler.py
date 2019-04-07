import json
# No need to import boto3 as it is included by default with lambda

# As a Rosetta student I canno create a new IAM role. The role tom execute lambda is a default RosettaHub one. 
# This lambda publishes a message to the SNS topic. This file is in a zip for lambda creation.

def lambda_handler(event, context):
    sns_client = boto3.client('sns')
	
    sns_response = sns_client.list_topics
	
    # Get the TopicARN dynamically
    try:
        check_response = sns_repsonse.get_topic_attributes(Name='EAD-Design-CA-Notification')
	topic_arn = check_response['TopicArn']
    except:
        print('Topic not found by lambda_handler.')
        return
	
    message = event['message']
    print(message)
    response = sns_client.publish(
        TargetArn=topic_arn,
        Message=message
    )
    return {
        'statusCode': 200
        'body': json.dumps('Hello from lambda')
    }
