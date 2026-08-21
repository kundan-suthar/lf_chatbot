import boto3
from collections.abc import Callable
from typing import Any


class BedrockClient:

    def __init__(
        self,
        region_name: str = "us-east-1",
    ):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region_name,
        )

    def converse(
        self,
        model_id: str,
        system_prompt: str,
        message: str,
    ) -> str:

        response = self.client.converse(
            modelId=model_id,
            system=[
                {
                    "text": system_prompt
                }
            ],
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

    def generate(self, message: str) -> str:
        return self.converse(
            model_id="google.gemma-3-12b-it",
            system_prompt="You are the Loanfront customer support assistant.",
            message=message,
        )

    def converse_with_tools(
        self,
        model_id: str,
        system_prompt: str,
        message: str,
        tools: list[dict[str, Any]],
        tool_executor: Callable[[str, dict[str, Any]], dict[str, Any]],
    ) -> str:
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": [{"text": message}],
            }
        ]

        while True:
            response = self.client.converse(
                modelId=model_id,
                system=[{"text": system_prompt}],
                messages=messages,
                toolConfig={
                    "tools": tools,
                    "toolChoice": {"auto": {}},
                },
            )
            assistant_message = response["output"]["message"]
            print(assistant_message)
            messages.append(assistant_message)

            tool_uses = [
                content["toolUse"]
                for content in assistant_message.get("content", [])
                if "toolUse" in content
            ]

            if not tool_uses:
                return "".join(
                    content.get("text", "")
                    for content in assistant_message.get("content", [])
                )

            tool_results = []

            for tool_use in tool_uses:
                result = tool_executor(
                    tool_use["name"],
                    tool_use.get("input", {}),
                )
                result_content = (
                    result
                    if isinstance(result, dict)
                    else {"data": result}
                )
                tool_results.append(
                    {
                        "toolResult": {
                            "toolUseId": tool_use["toolUseId"],
                            "content": [{"json": result_content}],
                        }
                    }
                )

            messages.append(
                {
                    "role": "user",
                    "content": tool_results,
                }
            )