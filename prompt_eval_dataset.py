import boto3
import json
import re, ast
from statistics import mean

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

def generate_dataset():
    prompt = """
    Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
    that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
    each representing task that requires Python, JSON, or a Regex to complete.

    Example output:
    ```json
    [
        {
            "task": "Description of task",
            "format": "json" or "python" or "regex",
            "solution_criteria": "Key criteria for evaluating the solution"
        },
        ...additional
    ]
    ```

    * Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
    * Focus on tasks that do not require writing much code

    Please generate 3 objects.
    """

    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    text = chat(messages, stop_sequence=["```"])
    return json.loads(text)



dataset = generate_dataset()
with open("prompt_eval_dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)


def run_prompt(test_case):  
    """ Merge prompt and test case input and return the result """
    
    prompt = f"""
    Your task is to complete the following task: {test_case['task']}
    * Respond only with Python, JSON or a plain Regex
    * Do not add any comments or explanations, just provide the code/JSON/Regex as output
    """ 
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```code")
    output = chat(messages, stop_sequence=["```"])
    return output

def model_grade(test_case, output):
    """ Grade the output based on the solution criteria in the test case """
    eval_prompt = f"""
    You are an expert AWS code reviewer. Your task is to evaluate the following AI-generated solution.

    Original Task:
    <task>
    {test_case["task"]}
    </task>

    Solution to Evaluate:
    <solution>
    {output}
    </solution>

    Criteria you should use to evaluate the solution:
    <criteria>
    {test_case["solution_criteria"]}
    </criteria>

    Output Format
    Provide your evaluation as a structured JSON object with the following fields, in this specific order:
    - "strengths": An array of 1-3 key strengths
    - "weaknesses": An array of 1-3 key areas for improvement
    - "reasoning": A concise explanation of your overall assessment
    - "score": A number between 1-10

    Respond with JSON. Keep your response concise and direct.
    Example response shape:
    {{
        "strengths": string[],
        "weaknesses": string[],
        "reasoning": string,
        "score": number
    }}
        """
    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")
    eval_response = chat(messages, stop_sequence=["```"])
    return json.loads(eval_response)

def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0


def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0


def validate_regex(text):
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0


def grade_syntax(response, test_case):
    format = test_case["format"]
    if format == "json":
        return validate_json(response)
    elif format == "python":
        return validate_python(response)
    else:
        return validate_regex(response)

def run_test_case(test_case):
    """ Calls run prompt and grades the result """
    output = run_prompt(test_case)

    #Grading 
    model_gradeing = model_grade(test_case, output)
    model_score = model_gradeing["score"]
    reasoning = model_gradeing["reasoning"]
    syntax_score = grade_syntax(output, test_case)
    score = (model_score + syntax_score) / 2

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning
    }

def run_eval(test_case):
    """ Loads the dataset and calls run_test_case for each test case, then returns the results """
    results = []
    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)
    average_score = mean([result['score'] for result in results])
    print(f"Average Score: {average_score}")
    return results

run_eval_results = run_eval(dataset)
print(json.dumps(run_eval_results, indent=2))