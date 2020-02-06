import boto3
import os
import json
import time

from boto3.dynamodb.conditions import Key

dynamodb = boto3.client('dynamodb')
ddb_r = boto3.resource('dynamodb')
table = ddb_r.Table(os.environ['DYNAMODB_TABLE'])


def handler(event, context):
    now = int(time.time())
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
        phone_data = result[0]
        has_voted = phone_data['hasVoted']
        verification_code = phone_data['verificationCode']
        code_age_seconds = now - int(phone_data['updatedTime'])
    if has_voted:
        last_voted_time = phone_data["lastVotedTime"]
        time_since_last_vote = now - int(last_voted_time)
        # If the last vote was less than 5 min then block the vote
        if time_since_last_vote < 60 * 5:
            remaining_time = str(300 - time_since_last_vote)
            return generate_status_response("Looks like you've already voted recently! Please wait another " + remaining_time + " seconds")
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
    # After vote is recorded, update has_voted to true and update the lastVotedTime
    table.update_item(
        Key={
            'pk': phone_pk,
            'sk': phone_sk
        },
        UpdateExpression='SET hasVoted = :hasvotedtrue, lastVotedTime=:lastVotedTime',
        ExpressionAttributeValues={
            ':hasvotedtrue': True,
            ':lastVotedTime': str(int(time.time())),
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