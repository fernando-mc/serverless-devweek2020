import boto3
import os
import json
import random
import string
import time

from boto3.dynamodb.conditions import Key

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def handler(event, context):
    # Query for phone number (if it exists)
    # PHONE#phonenumber
    # SK = PHONE#ALL 
    phone_number = json.loads(event['body'])['phoneNumber']
    pk = 'PHONE#' + phone_number
    sk = 'PHONE#ALL'
    result = table.query(
       KeyConditionExpression=Key('pk').eq(pk) & Key('sk').eq(sk)
    )['Items']
    # If it doesn't exist - generate a code, create the record and text the code to the user
    if result == []:
        set_or_reset_code(phone_number)
        return create_response("Code sent!")
    # If the number exists and hasn't voted yet, send a new code
    if len(result) == 1:
        item = result[0]
        has_voted = item["hasVoted"]
    if not has_voted:
        set_or_reset_code(phone_number)
        return create_response("Code reset!")
    # Otherwise, do nothing
    return create_response("Your code is already used!")


def set_or_reset_code(phone_number):
    verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    table.put_item(
        Item = {
            'pk': 'PHONE#' + phone_number,
            'sk': 'PHONE#ALL',
            'phoneNumber': phone_number,
            'verificationCode': verification_code,
            'hasVoted': False,
            'updatedTime': str(int(time.time()))
        }
    )
    sns.publish(
        PhoneNumber=phone_number,
        Message="Your Serverless Jams verification code is: " + verification_code,
    )


def create_response(status):
    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin":"*"},
        "body": json.dumps({"status": status})
    }
