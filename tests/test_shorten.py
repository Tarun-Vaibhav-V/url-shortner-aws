import json, boto3, pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from moto import mock_aws
from src.shorten import handler


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        dynamodb.create_table(
            TableName='url-shortener-urls',
            KeySchema=[{'AttributeName': 'short_code', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'short_code', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        yield


def test_shorten_valid_url(dynamodb_table):
    event = {'body': json.dumps({'url': 'https://github.com'})}
    result = handler(event, None)
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert 'short_url' in body
    assert len(body['code']) == 6


def test_shorten_invalid_url(dynamodb_table):
    event = {'body': json.dumps({'url': 'not-a-url'})}
    result = handler(event, None)
    assert result['statusCode'] == 400
