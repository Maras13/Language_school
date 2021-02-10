import json
import boto3

TABLE_NAME = 'EmailAddresses'
dynamo_table = boto3.resource('dynamodb').Table('EmailAddresses')
dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):

    needs_email = get_items_needing_email()
    

    return {
        'statusCode': 200,
        'body': json.dumps()
    }

def get_items_needing_email():
    resp = dynamo_table.scan()

    return resp
