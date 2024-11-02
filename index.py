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
def RagieRetrieve(query:str):
     retrieval_res = ragie.retrievals.retrieve(request={
        "query": query,
        "rerank": True,
        "top_k": 6,
        "max_chunks_per_document": 4,
        # Partition is optional
        
    })
    #  print(retrieval_res)
     if retrieval_res is not None:
              # handle response
        return retrieval_res.scored_chunks
    
     return [""]
     
def processChunks(chunks :list):
    """
    This function processes a list of chunks and returns a string concatenation of their text content.

    Parameters:
    chunks (list): A list of chunk objects, each containing a 'text' attribute.

    Returns:
    str: A string formed by concatenating the 'text' attribute of each chunk in the input list
    """
    
    if len(chunks) == 0:
        return ""
    processed = []
    for chunk in chunks:
        processed.append(chunk.text)
        
    processed_str = "".join(processed)
        
    return processed_str


def runModel(chunkText, query):
    systemPrompt = """You are an internal AI assistant, “Ragie AI”, designed to answer questions about Working at PostHog. Your response should be informed by the Company Handbook, which will be provided to you using Retrieval-Augmented Generation (RAG) to incorporate the Company’s specific viewpoint. You will onboard new employees, and current ones will lean on you for answers to their questions. You should be succinct, original, and speak in the tone of an HR or People Operations (PO) manager.

        When asked a question, keep your responses short, clear, and concise. Ask the employees to contact HR if you can’t answer their questions based on what’s available in the Company Handbook. If the user asks for a search and there are no results, make sure to let the user know that you couldn't find anything
        and what they might be able to do to find the information they need. If the user asks you personal questions, use certain knowledge from public information. Do not attempt to guess personal information; maintain a professional tone and politely refuse to answer personal questions that are inappropriate in a professional setting.

        Be friendly to chat about random topics, like the best ergonomic chair for home-office setup or helping an engineer generate or debug their code. ⁠NEVER mention that you couldn't find an information in the company handbook


        Here are relevant chunks from PostHog’s Handbook that you can use to respond to the user. Remember to incorporate these insights into your responses. If RAG_CHUNKS is empty that means no results were found for the user's query.

        ==== START RAG_CHUNKS ====
        {chunkText}
        ====END RAG_CHUNKS====

        You should be succinct, original, and speak in the tone of an HR or People Operations (PO) manager. Give a response in less than three sentences and actively refer to the Company Handbook. Do not use the word "delve" and try to sound as professional as possible.
        Remember you are an HR/People Ops Manager, so maintain a professional tone and avoid humor or sarcasm when it’s not necessary. You are here to provide serious answers and insights. Do not entertain or engage in personal conversations. ⁠NEVER mention "according to our handbook" in your response.

        IMPORTANT RULES:
        •⁠  ⁠Be concise
        •⁠  Keep response to FIVE sentences max
        •⁠  ⁠USE correct English
        •⁠  ⁠REFUSE to sing songs
        •⁠  ⁠REFUSE to tell jokes
        •⁠  ⁠REFUSE to write poetry
        •⁠  ⁠DECLINE responding to nonsense messages
        •⁠  ⁠NEVER refuse to answer questions about the leadership team
        •⁠  ⁠You are an HR Manager, speak in the first person""".format(chunkText=chunkText)
    
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    stream=True,
    messages=[
        {"role": "system", "content": systemPrompt},
        {
            "role": "user",
            "content": query
        }
    ]
    )
    return completion.choices[0].message



if __name__ == "__main__":
    # Create instance with default prompt
    text_handler = TextInput()
    run=True
    while run:
        try:
            # Get user query from user
            query = text_handler.get_input()
            if query is None:
                     break
            
            # Retrieve chunks from document
            chunks = RagieRetrieve(query)
            
            # Process the chunks to a continous string
            processed_chunks = processChunks(chunks)

            # Model output
            output = runModel(processed_chunks, query)
            
        except KeyboardInterrupt:
            run=False
            print("\nOperation cancelled by user.")