terraform {
  required_version = ">= 0.14"
}

provider "aws" {
  region  = "eu-central-1"
}

resource "aws_dynamodb_table" "NatebotEmailTable" {
  name = "NatebotEmailTable"
  hash_key         = "Email"
  billing_mode     = "PAY_PER_REQUEST"

  attribute {
    name = "Email"
    type = "S"
  }
}