import openai
import os
import json

# Setup OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Constants
SYSTEM_MESSAGE = "You are Yahya AI,An AI assistant helping recruiters & Talent Acquisition teams analyse and query about Yahya Ghani's Career trajectory to better assess their suitability for possible vacancies in their organisations. You are often provided Career Documentation from Yahya Ghani's CV and other career documents to help you answer the queries."
# MAX_CALLS = 5
client = openai

# Function to call OpenAI with provided messages and functions
def get_openai_response(messages, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
    )
    print(f"OpenAI response: {response}")  # Debugging statement
    answer_json_string=(response.model_dump_json(indent=2))
    answer_dict = json.loads(answer_json_string)
    answer = answer_dict['choices'][0]['message']['content']
    print('answer of summary jsonify',answer)
    return answer

# Function to query OpenAI with chunks
def query_openai_with_chunks(query_text, chunk_texts):
    # Combine the query text with the chunk texts for OpenAI
    combined_text = f"Query: {query_text}\n\Context:\n" + "\n\n".join(chunk_texts)
    
    # Build the messages
    messages = [
        {"content": SYSTEM_MESSAGE, "role": "system"},
        {"content": combined_text, "role": "user"},
    ]
    
    # Get OpenAI response
    response = get_openai_response(messages)
    print(f"Final Response : {response}\n")

    # Extract and return the response content
    return response
