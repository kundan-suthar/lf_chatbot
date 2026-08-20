import os

import boto3


class EmbeddingClient:

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION"),
        )

        self.model_id = os.getenv(
            "BEDROCK_EMBEDDING_MODEL_ID",
            "amazon.titan-embed-text-v2:0",
        )

    def embed(self, text: str) -> list[float]:

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=__import__("json").dumps({
                "inputText": text,
                "dimensions": 1024,
                "normalize": True,
            }),
            contentType="application/json",
            accept="application/json",
        )

        body = __import__("json").loads(
            response["body"].read()
        )

        return body["embedding"]