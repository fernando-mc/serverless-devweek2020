import boto3
import os
import json

from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])


def handler(event, context):
    pk = "SONGS#ALL"
    result = table.query(
       KeyConditionExpression=Key('pk').eq(pk)
    )
    song_votes = []
    for item in result["Items"]:
        song_votes.append({
            "songName": item["sk"][5:],
            "votes": str(item["votes"])
        })
    response = {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin":"*"},
        "body": json.dumps(song_votes)
    }
    return response
