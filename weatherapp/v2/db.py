import boto3
import pytz
from datetime import datetime
from botocore.exceptions import ClientError
import sys

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('weather')
id =  1
cst = pytz.timezone('America/Chicago')
now = datetime.now(cst)
current_date = now.strftime('%Y-%m-%d')
current_time = now.strftime('%H:%M:%S')


def write_to_weather(location,current,ftemp,ctemp):
    print(location,current,ftemp,ctemp, file=sys.stderr)
    result = location.split(",")
    if len(result) == 3:
        city, state, country = result
    else:
        city, country = result
        state = ''
    try:
        response = table.put_item(
                Item = {
                    'id': id,
                    'location': location,
                    'city': city,
                    'state': state,
                    'country': country,
                    'current': current,
                    'ftemp': ftemp,
                    'ctemp': ctemp,
                    'date': current_date,
                    'time': current_time,
                }
            )
        return response
    except ClientError as e:
        print(f"Error: {e.response['Error']['Message']}")