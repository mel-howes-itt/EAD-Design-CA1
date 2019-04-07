import boto3
import json

def ActivateLambdaNotification(outputMessage):
    # Get the lambda ARN dynamically
    lambda_client = boto3.client('lambda')

    try:
        lambda_response = lambda_client.get_function(FunctionName='Test-Function1')
        myFunctionARN = lambda_response['Configuration']['FunctionArn']
    except:
        print('Function not found by ActivateLambdaNotification.')
        return

    payload = {}
    payload['message'] = outputMessage
    response = lambda_client.invoke(
        FunctionName=myFunctionARN,
        InvocationType='RequestResponse',
        LogType='Tail',
        Payload=json.dumps(payload)
    )
    print('Sending notification to lambda.')

