import boto3


class BedrockClient:

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
        )

        self.model_id = "us.amazon.nova-2-lite-v1:0"

    def generate(self, message: str) -> str:
        response = self.client.converse(
            modelId=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": message
                        }
                    ],
                }
            ],
        )

        return response["output"]["message"]["content"][0]["text"]