import os
import json

# TODO load environment in beginning of app, currently loads in ultiple places, unnecessary
from dotenv import load_dotenv
load_dotenv()

from boto3 import Session
session = Session(
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)
bedrock = session.client('bedrock-runtime')

async def get_streaming_chat_response(prompt, max_tokens=3000):
    body = json.dumps({
        "prompt": "Human:" + prompt + "\n\nAssistant:",
        "max_tokens_to_sample": max_tokens,
    })
    response = bedrock.invoke_model_with_response_stream(
        body=body,
        modelId=os.getenv('CLAUDE_INSTANT_MODEL'),
        contentType='application/json',
    )
    for event in response['body']:
        yield "data: " + event['chunk']['bytes'].decode() + "\n\n"

# TODO Why top_p 90% ?
def get_chat_response(prompt, max_tokens=3000, temperature=1.0, top_p=0.9):
    body = json.dumps({
        "prompt": "Human:" + prompt + "\n\nAssistant:",
        "max_tokens_to_sample": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    })
    response = bedrock.invoke_model(
        body=body,
        modelId=os.getenv('CLAUDE_INSTANT_MODEL'),
        accept='application/json',
        contentType='application/json',
    )
    response_body = json.loads(response.get('body').read())
    return response_body.get('completion')
