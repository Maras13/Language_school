# This is the lambda code that will accept JSON from API Gateway 
# and add the users into the DynamoDB Table specified by TABLE_NAME

import json
import boto3

TABLE_NAME = 'NatebotEmailTable'
dynamo_table = boto3.resource('dynamodb').Table('NatebotEmailTable')
dynamo = boto3.client('dynamodb')
ses = boto3.client('ses')

def lambda_handler(event, context):

    try:
        # Input validation
        event = validate_input(event)

        # Update item "days" field in DDB if exist already
        if exists(event['Email']):
            
            response = dynamo_table.update_item(
                Key={'Email': event['Email']},
                UpdateExpression="set days = :d",
                ExpressionAttributeValues={
                    ':d': event['days']
                },
                ReturnValues="UPDATED_NEW"
            )
        # Otherwise insert item into DDB table, SES, and send verification email
        else:
            # TODO: Move this to some Cloudwatch logging, return something useful
            response = dynamo_table.put_item(Item=event)

            response = ses.send_custom_verification_email(
                EmailAddress=event['Email'],
                TemplateName='VerificationTemplate'
            )
        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }
    except Exception as e:
        return {
        "statusCode": 500,
        "body": str(e)
    }

def exists(name):
    response = dynamo.get_item(
        Key={
            'Email': {
                'S': name,
            },
        },
        TableName=TABLE_NAME,
    )
    if 'Item' in response:
        return response['Item']
    else:
        return None

# Make sure that:
# 1. Both email and days are provided
# 2. The values provided are strings
def validate_input(event):
    if event["queryStringParameters"] == None:
        raise Exception("ERROR: {}".format("No Arguments passed! Please pass required arguments 'Email' and 'Days'"))

    event = event['queryStringParameters']

    if "Email" not in event or "Days" not in event:
        raise Exception("ERROR: {}".format("Please pass required arguments 'Email' and 'Days'"))

    if not isinstance(event["Email"], str) or not isinstance(event["Days"], str):
        raise Exception("ERROR: {}".format("Value of 'Email' and 'Days' must be type: String"))

    return event