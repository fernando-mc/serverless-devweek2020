import boto3
import os
import json
import time

from boto3.dynamodb.conditions import Key

dynamodb = boto3.client('dynamodb')
ddb_r = boto3.resource('dynamodb')
table = ddb_r.Table(os.environ['DYNAMODB_TABLE'])


def handler(event, context):
    body = json.loads(event['body'])
    unverified_code = body['verificationCode']
    phone_number = body['phoneNumber']
    song_name = body['songName']
    phone_pk = "PHONE#" + phone_number
    phone_sk = "PHONE#ALL"
    result = table.query(
       KeyConditionExpression=Key('pk').eq(phone_pk) & Key('sk').eq(phone_sk)
    )['Items']
    if result == []:
        return generate_status_response("We can't find a verification code, did you enter your phone number?")
    if result:
        has_voted = result[0]['hasVoted']
        verification_code = result[0]['verificationCode']
        code_age_seconds = int(time.time()) - int(result[0]['updatedTime'])
    if has_voted:
        return generate_status_response("It looks like this number has already voted!")
    if verification_code != unverified_code:
        return generate_status_response("The code you entered is not correct.")
    if code_age_seconds > (60 * 5):
        return generate_status_response("The code you entered has expired, try creating a new one.")
    # If all checks pass, record the vote
    result = table.update_item(
        TableName=os.environ['DYNAMODB_TABLE'],
        Key={
            'pk': 'SONGS#ALL',
            'sk': 'SONG#' + song_name
        },
        UpdateExpression='ADD votes :inc',
        ExpressionAttributeValues={
            ':inc': 1
        },
        ReturnValues="UPDATED_NEW"
    )
    # After vote is recorded, update has_voted to true
    table.update_item(
        Key={
            'pk': phone_pk,
            'sk': phone_sk
        },
        UpdateExpression='SET hasVoted = :hasvotedtrue',
        ExpressionAttributeValues={
            ':hasvotedtrue': True
        }
    )
    # Return the successful response with the new vote count
    response = {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"votes": str(result["Attributes"]["votes"])})
    }
    return response

def generate_status_response(status):
    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"status": status})
    }