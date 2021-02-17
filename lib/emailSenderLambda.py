import json
import boto3
import datetime

TABLE_NAME = 'NatebotEmailTable'
dynamo_table = boto3.resource('dynamodb').Table('NatebotEmailTable')
dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):

    needs_email = get_items_needing_email()
    
    send_emails(needs_email)

    return {
        'statusCode': 200,
        'body': json.dumps(needs_email)
    }

def get_items_needing_email():
    resp = dynamo_table.scan()
    needs_email = []
    for email in resp["Items"]:
        
        # Check if Welcome email needs to be sent
        if "LastEmailDate" not in email:
            needs_email.append(email)

        # Check if "Days" have elapsed and a new email needs to be sent
        else:
            time_delta = datetime.datetime.now() - datetime.strptime(email["LastEmailDate"], "%d %B, %Y")
            if time_delta.days >= email["Days"] :
                needs_email.append(email)
            
    return needs_email

def send_emails(emails):
    return False