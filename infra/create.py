#!/usr/bin/env python3
# 
# This script creates an email newsletter service using AWS Services 

from python_terraform import *
import boto3
import os

def main():
    """ Uses Terraform and AWS CLI to bootstrap resources """
    # Terraform
    print("-> Terraforming...")
    cwd = os.getcwd()
    t = Terraform(working_dir=cwd)
    t.init()
    return_code, stdout, stderr = t.apply(skip_plan=True)
    if return_code == 0:
        out = stdout.split("Apply complete!")[1]
        print(out)
    else:
        print("ERROR {}: {}".format(return_code, stderr))

    # AWS CLI 
    print("-> Deploying resources with AWS CLI...")
    ses_client = boto3.client('ses')
    try:
        check_if_template_exists = ses_client.get_custom_verification_email_template(
            TemplateName='VerificationTemplate'
        )
    except ses_client.exceptions.CustomVerificationEmailTemplateDoesNotExistException as e:
        from_email_address = input("Your email address: ")
        try:
            response = ses_client.create_custom_verification_email_template(
                TemplateName='VerificationTemplate',
                FromEmailAddress=from_email_address,
                TemplateSubject='Please confirm your email address for NateBot',
                TemplateContent="""<html>
                                <head></head>
                                <body style='font-family:sans-serif;'>
                                <h1 style='text-align:center'>Ready to start sending 
                                email with NateBot?</h1>
                                <p>We here at Example Corp are happy to have you on
                                board! There's just one last step to complete before
                                you can start sending email. Just click the following
                                link to verify your email address. Once we confirm that 
                                you're really you, we'll give you some additional 
                                information to help you get started with ProductName.</p>
                                </body>
                                </html>""",
                SuccessRedirectionURL='https://www.google.com',
                FailureRedirectionURL='https://www.google.com'
            )
            print(response)
        except ses_client.exceptions.FromEmailAddressNotVerifiedException as e:
            print("ERROR: Go to your email ({}) and complete verification first!".format(from_email_address))

    sesv2_client = boto3.client('sesv2')
    website_url = input("Your website URL (https://www.[yourwebsite].com): ")
    response = sesv2_client.put_account_details(
        MailType='TRANSACTIONAL',
        WebsiteURL=website_url,
        ContactLanguage='EN',
        UseCaseDescription='Educational newsletter',
        ProductionAccessEnabled=True
    )

if __name__ == "__main__":
    main()