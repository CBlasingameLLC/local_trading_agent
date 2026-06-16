import ollama

def test_agent_connection():
    print("Initializing connection to local Llama 3 model...")
    
    # We send a structured prompt to the local Ollama server
    response = ollama.chat(model='llama3', messages=[
        {
            'role': 'system',
            'content': 'You are a highly analytical financial assistant.'
        },
        {
            'role': 'user',
            'content': 'Explain the concept of delta-neutral trading in two sentences.'
        }
    ])
    
    # Extract and print the model's response
    print("\nAgent Response:")
    print(response['message']['content'])

if __name__ == "__main__":
    test_agent_connection()