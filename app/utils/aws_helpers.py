import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_aws_credentials():
    """
    Get AWS credentials from environment variables or instance profile.
    """
    return {
        'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'aws_session_token': os.environ.get('AWS_SESSION_TOKEN'),
        'region_name': os.environ.get('AWS_REGION', 'us-east-1')
    }


def create_s3_client():
    """
    Create an S3 client using environment credentials.
    """
    try:
        return boto3.client('s3', **get_aws_credentials())
    except Exception as e:
        logger.error(f"Error creating S3 client: {e}")
        raise


def upload_to_s3(file_data, bucket_name, object_key):
    """
    Upload a file to an S3 bucket.
    """
    s3_client = create_s3_client()
    try:
        s3_client.put_object(
            Body=file_data,
            Bucket=bucket_name,
            Key=object_key
        )
        return f"s3://{bucket_name}/{object_key}"
    except ClientError as e:
        logger.error(f"Error uploading to S3: {e}")
        raise


def download_from_s3(bucket_name, object_key):
    """
    Download a file from an S3 bucket.
    """
    s3_client = create_s3_client()
    try:
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=object_key
        )
        return response['Body'].read()
    except ClientError as e:
        logger.error(f"Error downloading from S3: {e}")
        raise
