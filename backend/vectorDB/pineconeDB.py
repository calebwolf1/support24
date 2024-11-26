from pinecone import Pinecone, ServerlessSpec
from llama_index.core import SimpleKeywordTableIndex, Document
import openai
import dotenv
import os
import asyncio
from sklearn.metrics.pairwise import cosine_similarity

dotenv.load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment="us-east-1")
index_name = "sources"

# All users will share the sources index but have a namespace based on user_id for separation
# Inferences will only be made within the user's namespace's sources

#only run this once to create the index

# if index_name not in pc.list_indexes():
#     pc.create_index(
#         name=index_name,
#         dimension=1536,  # OpenAI text-embedding-ada-002 has 1536 dimensions
#         metric='cosine',  # Use cosine for semantic search
#         spec=ServerlessSpec(
#             cloud="aws",  # Pinecone configures AWS for you
#             region="us-east-1"
#         )
#     )

index = pc.Index(index_name)
openai.api_key = os.getenv("OPENAI_API_KEY")

def embed_text(text):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]  # Passing the text inside a list as the new API expects a list of inputs
    )
    return response.data[0].embedding  # Accessing the embedding from the response using the .data attribute

async def add_sources_to_pinecone(user_id, sources):
    """Embed and store trusted sources in Pinecone for a specific user."""
    namespace = f"user_{user_id}"
    for source_id, content in sources.items():
        embedding = embed_text(content)
        index.upsert([(source_id, embedding, {"content": content})], namespace=namespace)
    
    # Wait to ensure data is indexed before querying
    await wait_for_index_update(namespace)

async def wait_for_index_update(namespace, retries=10, delay=2):
    """Wait for Pinecone index to be updated."""
    for _ in range(retries):
        # Check if there are any items in the namespace
        result = index.query(vector=[0] * 1536, top_k=1, namespace=namespace)
        if result["matches"]:
            return True
        await asyncio.sleep(delay) # Wait for the index to be updated

def retrieve_sources_from_pinecone(user_id, claim, precomputed_claim_embedding=None):
    """Retrieve relevant sources for the claim using Pinecone for a specific user."""
    if precomputed_claim_embedding is None:
        precomputed_claim_embedding = embed_text(claim)

    namespace = f"user_{user_id}"
    search_results = index.query(vector=precomputed_claim_embedding, top_k=5, include_metadata=True, namespace=namespace)

    print("Pinecone search results:", search_results)  # Debugging line

    return [result["metadata"]["content"] for result in search_results["matches"]]

def fact_check_with_llama(claim, sources, claim_embedding=None, source_embeddings=None):
    """Use LlamaIndex to fact-check the claim against the sources."""
    # If embeddings are not precomputed, compute them
    if claim_embedding is None:
        claim_embedding = embed_text(claim)
    if source_embeddings is None:
        source_embeddings = [embed_text(source) for source in sources]
    
    # Compute cosine similarity between the claim and sources
    similarities = cosine_similarity([claim_embedding], source_embeddings)
    print("Cosine Similarity between claim and sources:", similarities)  # Debugging line

    # Convert sources into Documents for LlamaIndex
    documents = [Document(text=source) for source in sources]
    
    # Create the index and the query engine
    index = SimpleKeywordTableIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    response = query_engine.query(claim)
    return response.response  # fact-checking result

async def main():
    # Example trusted sources (in practice, use a database or files)
    trusted_sources = {
    "source_1": "The earth revolves around the sun in an elliptical orbit and is not circular.",
    "source_2": "Water boils at 100 degrees Celsius at sea level but freezes at 0 degrees.",
    "source_3": "The capital of France is Paris and eggs are oval shaped."
    }
    
    # Example user_id (in a real-world scenario, this would be dynamically generated or provided)
    user_id = 1244  # currently using for testing
    
    # Add trusted sources to Pinecone for the user
    await add_sources_to_pinecone(user_id, trusted_sources)
    
    # Retrieve sources relevant to the claim for the user
    user_claim = "The capital of England is Sweden."

    # Precompute claim embedding once for later use
    claim_embedding = embed_text(user_claim)

    relevant_sources = retrieve_sources_from_pinecone(user_id, user_claim, precomputed_claim_embedding=claim_embedding)
     # Precompute source embeddings once for later use
    source_embeddings = [embed_text(source) for source in relevant_sources]

    fact_check_result = fact_check_with_llama(user_claim, relevant_sources, claim_embedding, source_embeddings)
    
    # Output the result
    print("Claim:", user_claim)
    print("Fact-Check Result:", fact_check_result)

if __name__ == "__main__":
    asyncio.run(main())