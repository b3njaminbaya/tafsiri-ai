import boto3
from botocore.client import Config

from .core.config import settings


def get_s3_client():
    """Internal client (container-network endpoint) for actual put/get calls."""
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_endpoint_url,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
        region_name=settings.minio_region,
    )


def get_s3_public_client():
    """Client configured with the browser-reachable endpoint — used only to
    generate presigned URLs, never for server-side put/get.
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_public_url,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
        region_name=settings.minio_region,
    )
