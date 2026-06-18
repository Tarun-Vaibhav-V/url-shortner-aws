import json, boto3, pytest, sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from moto import mock_aws
from src.redirect import handler


@pytest.fixture
def tables():
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        urls = dynamodb.create_table(
            TableName='url-shortener-urls',
            KeySchema=[{'AttributeName': 'short_code', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'short_code', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        clicks = dynamodb.create_table(
            TableName='url-shortener-clicks',
            KeySchema=[
                {'AttributeName': 'short_code', 'KeyType': 'HASH'},
                {'AttributeName': 'click_id', 'KeyType': 'RANGE'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'short_code', 'AttributeType': 'S'},
                {'AttributeName': 'click_id', 'AttributeType': 'S'},
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        urls.put_item(Item={
            'short_code': 'abc123',
            'original_url': 'https://example.com',
            'created_at': int(time.time()),
            'ttl': int(time.time()) + 86400
        })
        yield


def test_redirect_existing_code(tables):
    event = {
        'pathParameters': {'code': 'abc123'},
        'headers': {'User-Agent': 'Mozilla/5.0', 'CloudFront-Viewer-Country': 'IN'}
    }
    result = handler(event, None)
    assert result['statusCode'] == 301
    assert result['headers']['Location'] == 'https://example.com'


def test_redirect_missing_code(tables):
    event = {
        'pathParameters': {'code': 'XXXXXX'},
        'headers': {}
    }
    result = handler(event, None)
    assert result['statusCode'] == 404
