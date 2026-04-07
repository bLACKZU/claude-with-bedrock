import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')
# model_id = "us.anthropic.claude-3-haiku-20240307-v1:0"
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

def add_assistant_message(messages, text):
    assistant_message = {
        "role": "assistant",
        "content": [
            {
                "text": text
            }
        ]
    }
    messages.append(assistant_message)

def chat(messages, system_prompt=None, temperature=1.0, stop_sequence=[]):
    params = {
        "modelId": model_id,
        "messages": messages,
        "inferenceConfig": {
            "temperature": temperature,
            "stopSequences": stop_sequence
        }
    }
    if system_prompt:
        params["system"] = [{"text": system_prompt}]
    try:
        print("Sending request to Bedrock...")
        response = client.converse(**params)
    
        return response['output']['message']['content'][0]['text']

    except Exception as e:
        print(f"An error occurred: {e}")

messages = []
prompt = """
Generate three different sample AWS CLI commands. Each should be very short
"""
add_user_message(messages, prompt)
add_assistant_message(messages, "Here are three sample AWS CLI commands without any comments:\n\n```bash")
text = chat(messages, stop_sequence=["```"])
print(text)

