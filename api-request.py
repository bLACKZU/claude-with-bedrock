import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')
model_id = "us.anthropic.claude-3-haiku-20240307-v1:0"

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

def chat(messages):
    try:
        print("Sending request to Bedrock...")
        response = client.converse(
            modelId=model_id,
            messages=messages
        )
    
        return response['output']['message']['content'][0]['text']

    except Exception as e:
        print(f"An error occurred: {e}")

messages = []
add_user_message(messages, "Whats 1 + 1?") 
answer = chat(messages) 
add_assistant_message(messages, answer)
add_user_message(messages, "Add 3 more to that")
answer = chat(messages)
print(answer)  