import json
import logging
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    database_url: str
    aws_region: str = "ap-south-1"
    s3_bucket_name: str
    jwt_secret: str
    log_level: str = "INFO"
    environment: str = "dev"

    model_config = {"env_file": ".env", "extra": "ignore"}


def _fetch_secret(secret_name: str, region: str) -> dict:
    client = boto3.client("secretsmanager", region_name=region)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        logger.error("Failed to fetch secret %s: %s", secret_name, e)
        raise


@lru_cache
def get_settings() -> Settings:
    """
    In production (ENVIRONMENT != dev) pull JWT_SECRET and DATABASE_URL
    from Secrets Manager so they never live in environment variables.
    """
    base = Settings()  # type: ignore[call-arg]

    if base.environment != "dev":
        secrets = _fetch_secret("mxtz/backend", base.aws_region)
        return Settings(
            database_url=secrets["database_url"],
            aws_region=base.aws_region,
            s3_bucket_name=secrets.get("s3_bucket_name", base.s3_bucket_name),
            jwt_secret=secrets["jwt_secret"],
            log_level=base.log_level,
            environment=base.environment,
        )

    return base
