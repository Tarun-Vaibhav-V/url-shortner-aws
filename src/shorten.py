import json, boto3, hashlib, os, time

TABLE = os.environ.get('URLS_TABLE', 'url-shortener-urls')
BASE_URL = os.environ.get('BASE_URL', 'https://your-api-id.execute-api.ap-south-1.amazonaws.com/prod')


def generate_code(url: str) -> str:
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    digest = int(hashlib.sha256(url.encode()).hexdigest(), 16)
    code = ''
    for _ in range(6):
        code += chars[digest % 62]
        digest //= 62
    return code


def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        url = body.get('url', '').strip()
        if not url or not url.startswith(('http://', 'https://')):
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid URL'})}
        code = generate_code(url)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(TABLE)
        table.put_item(Item={
            'short_code': code,
            'original_url': url,
            'created_at': int(time.time()),
            'ttl': int(time.time()) + 60 * 60 * 24 * 365
        })
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'short_url': f'{BASE_URL}/{code}', 'code': code})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
