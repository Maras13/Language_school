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
    sesv2_client = boto3.client('sesv2')

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
                TemplateSubject='Please confirm your email address for Language Bootcamp',
                TemplateContent="""<html>
                                <head></head>
                                <body style='font-family:sans-serif;'>
                                <h1 style='text-align:center'>Confirm email address for Language Bootcamp</h1>
                                <p>Hi there,
                                Great to have you on board.  Please click the following link to verify your email and, once we confirm that you're really you, 
                                we'll get you started with the exercises.</p>
                                </body>
                                </html>""",
                SuccessRedirectionURL='https://www.google.com',
                FailureRedirectionURL='https://www.google.com'
            )
            print(response)
        except ses_client.exceptions.FromEmailAddressNotVerifiedException as e:
            print("ERROR: Go to your email ({}) and complete verification first!".format(from_email_address))

    response = sesv2_client.get_account()
    if response['ProductionAccessEnabled'] == False:
        website_url = input("Your website URL (https://www.[yourwebsite].com): ")
        response = sesv2_client.put_account_details(
            MailType='TRANSACTIONAL',
            WebsiteURL=website_url,
            ContactLanguage='EN',
            UseCaseDescription='Educational newsletter',
            ProductionAccessEnabled=True
        )
        print(
            """
            Now please go to your AWS Account and then Services -> Simple Email Service (SES) -> Sending Statistics ->
            Your Account Details.  And fill out the form, for the description add this and an example of the first email newsletter you will use:

            I am creating a small email newsletter service that will send lessons by emails to my students based on how frequently (in days) they request them.  
            You can read more about the architecture of the service here: https://github.com/Maras13/Language_school_bot.

            The signup will be handled through my wordpress website, and will also give the option to unsubscribe through the website.

            The first email I will send to students is included below:\n\n
            """
        )
        throwaway = input("Done?")

if __name__ == "__main__":
    main()