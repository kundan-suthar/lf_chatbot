import os

import boto3
from botocore.exceptions import ClientError


class S3Client:

    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET_NAME")
        self.region = os.getenv("AWS_REGION")

        if not self.bucket:
            raise RuntimeError("S3_BUCKET_NAME is not configured")

        self.client = boto3.client(
            "s3",
            region_name=self.region,
        )

    def upload_file(
        self,
        file,
        s3_key: str,
    ) -> str:

        self.client.upload_fileobj(
            file,
            self.bucket,
            s3_key,
            ExtraArgs={
                "ContentType": "application/pdf",
            },
        )

        return f"s3://{self.bucket}/{s3_key}"