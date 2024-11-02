# Import all packages from the requirements.txt file using (pip install -r requirements.txt): 
import os
from openai import OpenAI
from ragie import Ragie
from dotenv import load_dotenv
# loading variables from .env file
load_dotenv() 

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

ragie = Ragie(
    auth=os.getenv('RAGIE_API_KEY'),
)

# Define the Text Input Class
class TextInput:
     def __init__(self, prompt="Enter text: "):
        self.prompt = prompt
        self.user_input = None
    
     def get_input(self):
        try:
            self.user_input = input(self.prompt)
            return self.user_input
        except EOFError:
            print("Error reading input")
            return None

# Function to retreieve from your already uploaded documents from Ragie
def Retrieve(query:str):
     retrieval_res = ragie.retrievals.retrieve(request={
        "query": query,
        "rerank": True,
        "top_k": 6,
        "max_chunks_per_document": 4,
        # Partition is optional
        
    })
     print(retrieval_res)
     return retrieval_res
     
     
def processChunks(chunks):
    return ""

def modelText(chunks):
    completion = client.chat.completions.create(
    model="gpt-4o",
    stream=True,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)
# Example usage
if __name__ == "__main__":
    # Create instance with default prompt
    text_handler = TextInput()
    result = text_handler.get_input()
    print("You entered:", result)