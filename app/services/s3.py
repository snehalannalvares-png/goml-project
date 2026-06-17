import logging

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_s3_client = None


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3", region_name=settings.aws_region)
    return _s3_client


async def upload_file(file_bytes: bytes, s3_key: str, content_type: str = "application/octet-stream") -> int:
    client = get_s3_client()
    try:
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=s3_key,
            Body=file_bytes,
            ContentType=content_type,
        )
        logger.info("Uploaded %d bytes to s3://%s/%s", len(file_bytes), settings.s3_bucket_name, s3_key)
        return len(file_bytes)
    except ClientError as e:
        logger.error("S3 upload failed for key %s: %s", s3_key, e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="File storage service unavailable",
        )


def generate_presigned_url(s3_key: str, expiry_seconds: int = 3600) -> str:
    client = get_s3_client()
    try:
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket_name, "Key": s3_key},
            ExpiresIn=expiry_seconds,
        )
    except ClientError as e:
        logger.error("Failed to generate presigned URL for %s: %s", s3_key, e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not generate download URL",
        )
