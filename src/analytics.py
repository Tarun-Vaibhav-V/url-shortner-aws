import json, boto3, os, time
from collections import Counter, defaultdict
from decimal import Decimal
from boto3.dynamodb.conditions import Key


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super().default(obj)


dynamodb = boto3.resource('dynamodb')
CLICKS_TABLE = os.environ.get('CLICKS_TABLE', 'url-shortener-clicks')


def handler(event, context):
    code = event['pathParameters']['code']
    try:
        table = dynamodb.Table(CLICKS_TABLE)
        resp = table.query(
            KeyConditionExpression=Key('short_code').eq(code)
        )
        items = resp.get('Items', [])
        if not items:
            return {'statusCode': 200, 'body': json.dumps({'total_clicks': 0})}

        countries = Counter(i.get('country', 'UNKNOWN') for i in items)
        devices = Counter(i.get('device', 'unknown') for i in items)

        now = int(time.time())
        hourly = defaultdict(int)
        for item in items:
            ts = int(item.get('timestamp', 0))
            if now - ts < 86400:
                hour = (ts % 86400) // 3600
                hourly[hour] += 1

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'short_code': code,
                'total_clicks': len(items),
                'by_country': dict(countries.most_common(10)),
                'by_device': dict(devices),
                'clicks_last_24h': dict(hourly)
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
