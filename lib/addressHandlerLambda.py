# This is the lambda code that will accept JSON from API Gateway 
# and add the users into the DynamoDB Table specified by TABLE_NAME
#
import json
import boto3

TABLE_NAME = 'EmailAddresses'
dynamo_table = boto3.resource('dynamodb').Table('EmailAddresses')
dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):
    
    if exists(event['email']):
        # Update item
        response = dynamo_table.update_item(
            Key={'email': event['email']},
            UpdateExpression="set days = :d",
            ExpressionAttributeValues={
                ':d': event['days']
            },
            ReturnValues="UPDATED_NEW"
        )
    else:
        # Insert item
        response = dynamo_table.put_item(Item=event)
    return response

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