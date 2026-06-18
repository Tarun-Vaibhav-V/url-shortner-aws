import json, boto3, os, time
from user_agents import parse as ua_parse

URLS_TABLE = os.environ.get('URLS_TABLE', 'url-shortener-urls')
CLICKS_TABLE = os.environ.get('CLICKS_TABLE', 'url-shortener-clicks')


def handler(event, context):
    code = event['pathParameters']['code']
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(URLS_TABLE)
        resp = table.get_item(Key={'short_code': code})
        item = resp.get('Item')
        if not item:
            return {'statusCode': 404, 'body': 'Not found'}

        headers = event.get('headers', {})
        ua_string = headers.get('User-Agent', '')
        ua = ua_parse(ua_string)
        device = 'mobile' if ua.is_mobile else 'tablet' if ua.is_tablet else 'desktop'
        country = headers.get('CloudFront-Viewer-Country', 'UNKNOWN')

        clicks = dynamodb.Table(CLICKS_TABLE)
        clicks.put_item(Item={
            'click_id': f'{code}#{int(time.time() * 1000)}',
            'short_code': code,
            'timestamp': int(time.time()),
            'country': country,
            'device': device,
            'ttl': int(time.time()) + 60 * 60 * 24 * 90
        })

        return {
            'statusCode': 301,
            'headers': {'Location': item['original_url']},
            'body': ''
        }
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}
