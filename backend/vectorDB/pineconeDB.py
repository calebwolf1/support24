from pinecone import Pinecone, ServerlessSpec
from llama_index.core import SimpleKeywordTableIndex, Document, ServiceContext
import openai
import dotenv
import os

dotenv.load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment="us-east-1")

index_name = "sources"
# if index_name not in pc.list_indexes():
#     pc.create_index(
#         name=index_name,
#         dimension=1536,  # openai text-embedding-ada-002 has 1536 dimensions
#         metric='cosine',  # use cosine for semantic search
#         spec=ServerlessSpec(
#             cloud="aws", # we do not need to configure aws, pinecone does it for us
#             region="us-east-1"
#         )
#     )
# else:
#     # TODO: ADD CHANGES TO SOURCES 
#     # print(f"Index '{index_name}' already exists.")
#     pass

index = pc.Index(index_name)
openai.api_key = os.getenv("OPENAI_API_KEY")

def embed_text(text):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]  # Passing the text inside a list as the new API expects a list of inputs
    )
    return response.data[0].embedding  # Accessing the embedding from the response using the .data attribute


def add_sources_to_pinecone(sources):
    """Embed and store trusted sources in Pinecone."""
    for source_id, content in sources.items():
        embedding = embed_text(content)
        index.upsert([(source_id, embedding, {"content": content})])

def retrieve_sources_from_pinecone(claim):
    """Retrieve relevant sources for the claim using Pinecone."""
    claim_embedding = embed_text(claim)
    search_results = index.query(vector=claim_embedding, top_k=5, include_metadata=True)
    return [result["metadata"]["content"] for result in search_results["matches"]]

def fact_check_with_llama(claim, sources):
    """Use LlamaIndex to fact-check the claim against the sources."""
    # Convert sources into Documents for LlamaIndex
    documents = [Document(text=source) for source in sources]
    
    # Create the index and the query engine
    index = SimpleKeywordTableIndex.from_documents(documents)
    
    # Create a query engine from the index
    query_engine = index.as_query_engine()
    
    # Query the claim using the query engine
    response = query_engine.query(claim)
    return response.response  # This contains the fact-checking result

# Main process
if __name__ == "__main__":
    # Example trusted sources (in practice, use a database or files)
    trusted_sources = {
        "source_1": "The earth revolves around the sun in an elliptical orbit.",
        "source_2": "Water boils at 100 degrees Celsius at sea level.",
        "source_3": "The capital of France is Paris."
    }
    
    # Add trusted sources to Pinecone
    # add_sources_to_pinecone(trusted_sources)
    
    # Example claim
    user_claim = "The earth revolves around the sun in a circular orbit."
    
    # Retrieve sources relevant to the claim
    relevant_sources = retrieve_sources_from_pinecone(user_claim)
    
    # Fact-check the claim using LlamaIndex
    fact_check_result = fact_check_with_llama(user_claim, relevant_sources)
    
    # Output the result
    print("Claim:", user_claim)
    print("Fact-Check Result:", fact_check_result)