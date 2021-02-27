import json
import boto3
import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = 'NatebotEmailTable'
dynamo_table = boto3.resource('dynamodb').Table('NatebotEmailTable')
dynamo = boto3.client('dynamodb')
s3 = boto3.client('s3')
sts = boto3.client('sts')
ses = boto3.client('ses')

def lambda_handler(event, context):

    needs_email = get_items_needing_email()
    logger.info("Found {} email addresses needing a new newsletter".format(len(needs_email)))
    
    if len(needs_email) > 0:
        send_emails(needs_email)

    
# Returns a list of DDB Items that need a new email sent
# ex) [
#       {"Email": "chancebair@gmail.com", "Days": "3"},
#       {"Email": "saramaras@gmail.com", "Days": "7", "LastEmail": "0-Welcome.html", "LastEmailSent": "2021-02-27 11:14:34.496160"}
#     ]
def get_items_needing_email():
    resp = dynamo_table.scan()
    needs_email = []
    for email in resp["Items"]:
        
        # Check if Welcome email needs to be sent
        if "LastEmailDate" not in email:
            logger.info("Email: {} needs Welcome email sent".format(email))
            needs_email.append(email)

        # Check if "Days" have elapsed and a new email needs to be sent
        else:
            time_delta = datetime.datetime.now() - datetime.datetime.strptime(email["LastEmailDate"], "%Y-%m-%d %H:%M:%S.%f")
            logger.info("time_delta: {}".format(time_delta))
            if time_delta.days >= int(email["Days"]) :
                logger.info("Required days ({}) have elapsed, new email must be sent".format(email["Days"]))
                needs_email.append(email)
            
    return needs_email

# Loop over Items from get_items_needing_email and send emails
def send_emails(emails):
    account_id = sts.get_caller_identity()['Account']
    bucket_name = "natebot-newsletter-bucket-" + account_id
    newsletters = s3.list_objects(Bucket=bucket_name)['Contents']
    logger.info("account_id: {}".format(account_id))
    logger.info("bucket_name: {}".format(bucket_name))
    logger.info("newsletters: {}".format(newsletters))

    for address in emails:
        # If an email hasn't been sent yet, get the Welcome email body
        if "LastEmail" not in address:
            logger.info("No field in LastEmail, getting Welcome email \"0-Welcome.txt\"")
            address["EmailBody"] = s3.get_object(Bucket=bucket_name, Key='0-Welcome.txt')['Body'].read().decode("utf-8") 
            address["NextNewsletter"] = "0-Welcome.txt"
            logger.info("Added EmailBody to: {}".format(address))
        # Otherwise get the next email body
        else: 
            next_email_index = int(address["LastEmail"][0]) + 1
            for newsletter in newsletters:
                next_newsletter_key = newsletter["Key"]
                if next_newsletter_key[0] == str(next_email_index):
                    logger.info("Found next newsletter ({}) for item: {}".format(next_newsletter_key, address))
                    address["NextNewsletter"] = next_newsletter_key
                    address["EmailBody"] = s3.get_object(Bucket=bucket_name, Key=next_newsletter_key)['Body'].read().decode("utf-8") 
                    logger.info("Added EmailBody to: {}".format(address))
    
        # If an Email Body wasn't found maybe the user has gotten the most recent newsletter so just warn
        if "EmailBody" not in address or "NextNewsletter" not in address:
            logger.warning("Unable to find next email to send for address: {}".format(address))
        # Otherwise send the email!
        else:
            from_email_address = ses.get_custom_verification_email_template(TemplateName='VerificationTemplate')["FromEmailAddress"]
            logger.info("SES FromEmailAddress: {}".format(from_email_address))

            send_email(address, from_email_address)

# Send email and update the DDB item
def send_email(to_address, from_address):
    try:
        response = ses.send_email(
            Destination={
                'ToAddresses': [
                    to_address["Email"]
                ],
            },
            Message={
                'Body': {
                    # 'Html': {
                    #     'Charset': 'UTF-8',
                    #     'Data': address["EmailBody"],
                    # },
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': to_address["EmailBody"],
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': 'New Lesson From Nate!',
                },
            },
            Source=from_address,
        )
        logger.info("Sent email to {}.  SES Response: {}".format(to_address["Email"], response))
        response = dynamo_table.update_item(
        Key={'Email': to_address["Email"]},
        UpdateExpression="set LastEmail = :e",
        ExpressionAttributeValues={
            ':e': to_address["NextNewsletter"]
        },
        ReturnValues="UPDATED_NEW"
        )
        logger.info("Update LastEmail: {}".format(response))
        response = dynamo_table.update_item(
            Key={'Email': to_address["Email"]},
            UpdateExpression="set LastEmailDate = :e",
            ExpressionAttributeValues={
                ':e': str(datetime.datetime.now())
            },
            ReturnValues="UPDATED_NEW"
        )
        logger.info("Update LastEmailDate: {}".format(response))
    except Exception as e:
        logger.error("Failed to send email! Error: {}".format(e))

    