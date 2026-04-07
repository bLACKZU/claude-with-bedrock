import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')
model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

def add_user_message(messages, text):
    user_message = {
        "role": "user",
        "content": [
            {
                "text": text
            }
        ]
    }
    messages.append(user_message)

messages = []
add_user_message(messages, "Write a 1 sentence description about John Summit, music producer and DJ")
text = ""
response = client.converse_stream(
    modelId=model_id, messages=messages)
for event in response['stream']:
    if 'contentBlockDelta' in event:
        delta_chunk = event['contentBlockDelta']['delta']['text']
        print(delta_chunk, end="")
        text += delta_chunk

print("\n\nFull response:\n" + text)