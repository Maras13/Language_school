# This is the lambda code that will accept JSON from API Gateway 
# and add the users into the DynamoDB Table specified by TABLE_NAME

import json
import boto3

TABLE_NAME = 'EmailAddresses'
dynamo_table = boto3.resource('dynamodb').Table('EmailAddresses')
dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):

    try:
        # Input validation
        event = validate_input(event)

        # Update item "days" field in DDB if exist already
        if exists(event['email']):
            
            response = dynamo_table.update_item(
                Key={'email': event['email']},
                UpdateExpression="set days = :d",
                ExpressionAttributeValues={
                    ':d': event['days']
                },
                ReturnValues="UPDATED_NEW"
            )
        # Otherwise insert item into DDB table
        else:
            response = dynamo_table.put_item(Item=event)
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
            'email': {
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
    event = event['queryStringParameters']

    if "email" not in event or "days" not in event:
        raise Exception("ERROR: {}".format("You must pass both 'email' and 'days'"))

    if not isinstance(event["email"], str) or not isinstance(event["days"], str):
        raise Exception("ERROR: {}".format("Value of 'email' and 'days' must be type: String"))

    return event