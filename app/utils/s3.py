import boto3
from botocore.config import Config
from datetime import datetime, timedelta
import uuid
from app.config import get_settings

settings = get_settings()

s3_client = boto3.client('s3',
                         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                         region_name=settings.AWS_REGION,
                         config=Config(signature_version='s3v4'))


def create_presigned_url(bucket: str,
                         key: str,
                         content_type: str,
                         expiration: int = 3600):
    """
    S3のプリサインドURLを生成する
    """
    params = {'Bucket': bucket, 'Key': key, 'ContentType': content_type}

    return s3_client.generate_presigned_url('put_object',
                                            Params=params,
                                            ExpiresIn=expiration)


def delete_s3_object(bucket: str, key: str):
    """
    S3のオブジェクトを削除する
    """
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        return True
    except Exception as e:
        print(f"Error deleting S3 object: {e}")
        return False
