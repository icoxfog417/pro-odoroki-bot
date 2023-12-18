import json
from typing import Optional
import boto3


class Bedrock():

    def __init__(self, region_name: Optional[str] = None) -> None:
        # Access to Amazon Bedrock
        # Please speficy region_name that model access is allowed, or preset it by aws configure. 
        self.client = boto3.client("bedrock-runtime", region_name=region_name)

    def ask_to_claude(self, message: str, 
                      version: str = "2",
                      instant: bool = True,
                      max_length:int = 1024,
                      temperature:float = 1.0,
                      top_p:float = 0.99) -> str:
        if instant:
            # instant is only v1
            model_id = "anthropic.claude-instant-v1"
        else:
            if version == "1":
                model_id = "anthropic.claude-v1"
            elif version == "2":
                model_id = "anthropic.claude-v2"
            elif version == "2.1":
                model_id = "anthropic.claude-v2:1"
            else:
                model_id = "anthropic.claude-v2"
        
        body = self._build_request_for_claude(message, max_length, temperature, top_p)
        response = self._send_message(model_id, body)
        response_body = json.loads(response.get("body").read())  # type: ignore
        reply = response_body.get("completion")
        return reply

    def _build_request_for_claude(self, message: str, max_length: int, temperature: float, top_p: float) -> dict:
        prompt = f"\n\nHuman: {message}\n\nAssistant:"
    
        body = {
            "prompt": prompt,
            "max_tokens_to_sample": max_length,
            "temperature": temperature,
            "top_p": top_p,
        }

        return body

    def _send_message(self, model_id: str, body: dict, accept: str = "application/json", content_type: str = "application/json") -> dict:
        response = self.client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            accept=accept,
            contentType=content_type,
        )
        
        return response
