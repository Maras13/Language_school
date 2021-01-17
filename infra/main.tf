terraform {
  required_version = ">= 0.14"
}

provider "aws" {
  region  = "eu-central-1"
}

# TODO: Add S3 Backend (maybe with a deploy script?)

# Dynamo DB Table
resource "aws_dynamodb_table" "NatebotEmailTable" {
  name = "NatebotEmailTable"
  hash_key         = "Email"
  billing_mode     = "PAY_PER_REQUEST"

  attribute {
    name = "Email"
    type = "S"
  }
}

# IAM User
resource "aws_iam_user" "NateBotUser" {
  name = "NateBotUser"
  path = "/"
}

resource "aws_iam_access_key" "NateBotUserKey" {
  user = aws_iam_user.NateBotUser.name
}

resource "aws_iam_user_policy_attachment" "NateBotPolicyAttachment" {
  user       = aws_iam_user.NateBotUser.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonAPIGatewayInvokeFullAccess"
}

output "NateBotUserSecretId" {
  value = aws_iam_access_key.NateBotUserKey.id
}

output "NateBotUserSecret" {
  value = aws_iam_access_key.NateBotUserKey.secret
}

# Lambda: Address Handler
resource "aws_iam_role" "NateBotAddressHandlerDDBRole" {
  name = "NateBotAddressHandlerDDBRole"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "NateBotAddressHandlerDDBRoleAttach1" {
  role       = aws_iam_role.NateBotAddressHandlerDDBRole.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_iam_role_policy_attachment" "NateBotAddressHandlerDDBRoleAttach2" {
  role       = aws_iam_role.NateBotAddressHandlerDDBRole.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

data "archive_file" "NateBotAddressHandlerZip" {
  source_dir  = "${path.module}/../lib/"
  output_path = "${path.module}/../lib/addressHandlerLambda.zip"
  type        = "zip"
}

# TODO: Add API Gateway Trigger
resource "aws_lambda_function" "NateBotAddressHandler" {
  filename      = data.archive_file.NateBotAddressHandlerZip.output_path
  function_name = "NateBotAddressHandler"
  role          = aws_iam_role.NateBotAddressHandlerDDBRole.arn
  handler       = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.NateBotAddressHandlerZip.output_base64sha256
  runtime = "python3.8"
}