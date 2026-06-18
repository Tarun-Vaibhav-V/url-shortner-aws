import os

# Set fake AWS credentials and region BEFORE any boto3/handler import.
# The Lambda runtime provides these in production; tests must set them so
# boto3.resource('dynamodb') (no explicit region) resolves to the same region
# moto creates the mock tables in.
os.environ.setdefault('AWS_DEFAULT_REGION', 'ap-south-1')
os.environ.setdefault('AWS_ACCESS_KEY_ID', 'testing')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'testing')
os.environ.setdefault('AWS_SECURITY_TOKEN', 'testing')
os.environ.setdefault('AWS_SESSION_TOKEN', 'testing')
