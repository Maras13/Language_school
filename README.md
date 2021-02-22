# Natebot
Design Doc: https://docs.google.com/document/d/13pL-B0ZmRjCw4SB9aJ3YBhiBD4HBVMISvPAAd1cqhwo

## Requirements
**Install**:
* terraform
* aws-cli

**Initialize**:
* `terraform init` in the infra dir
* AWS CLI pointing to aws account

## Setup
`cd infra`
`python3 -m pip install -r requirements.txt`
`python create.py`

## Architecture
### Lambda
There are two Lambda functions:
1. Address Handler (addressHandlerLambda)
Accepts users email and how frequently (in days) they want to receive emails, and adds this info into the database
2. Email Sender (emailSenderLambda)
Determines which email addresses in the database needs and email to be sent and sends the appropriate email.
### DynamoDB
The items in the DDB Table (NatebotEmailTable) are
* Email (STRING)
* Days (NUMBER)
* Last Email (STRING)
* Last Email Date (STRING)
### Amazon API Gateway
This allows for external web interfaces to call this infrastructure.  Takes the Email and Days, also an optional 
tag to remove email from the database.
