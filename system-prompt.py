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

def chat(messages, system_prompt=None, temperature=1.0):
    params = {
        "modelId": model_id,
        "messages": messages,
        "inferenceConfig": {
            "temperature": temperature
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
add_user_message(messages, "Generate a one-liner movie name for a movie about a dog who becomes a detective after struggle")
# text = chat(messages, system_prompt="Be very specific, do not add comments, I just want the code, and nothing else.")
text = chat(messages, temperature=0.7)
print(text)

