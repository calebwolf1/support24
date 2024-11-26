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

# Initialize Pinecone index
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
        await asyncio.sleep(delay)

def retrieve_sources_from_pinecone(user_id, claim, precomputed_claim_embedding=None):
    """Retrieve relevant sources for the claim using Pinecone for a specific user."""
    if precomputed_claim_embedding is None:
        precomputed_claim_embedding = embed_text(claim)

    namespace = f"user_{user_id}"
    search_results = index.query(vector=precomputed_claim_embedding, top_k=5, include_metadata=True, namespace=namespace)

    print("Pinecone search results:", search_results)  # Debugging line

    return [result["metadata"]["content"] for result in search_results["matches"]]

def chunk_text(text, chunk_size=100, overlap=20):
    """
    Break text into overlapping chunks.
    """
    words = text.split()
    chunks = [
        " ".join(words[i : i + chunk_size])
        for i in range(0, len(words), chunk_size - overlap)
    ]
    return chunks


def extract_relevant_snippets(claim, sources, claim_embedding=None, similarity_threshold=0.85):
    """
    Extract the most relevant snippets from sources based on cosine similarity.
    """
    if claim_embedding is None:
        claim_embedding = embed_text(claim)

    snippets = []
    for source in sources:
        # Chunk the source text into smaller segments
        chunks = chunk_text(source, chunk_size=50, overlap=20)
        
        # Embed each chunk
        chunk_embeddings = [embed_text(chunk) for chunk in chunks]
        
        # Compute cosine similarity
        similarities = cosine_similarity([claim_embedding], chunk_embeddings)[0]
        
        # Filter chunks by similarity threshold
        relevant_chunks = [
            (chunks[i], similarities[i])
            for i in range(len(chunks))
            if similarities[i] >= similarity_threshold
        ]
        
        # Add relevant chunks to the snippets list
        snippets.extend(relevant_chunks)
    
    # Sort snippets by similarity score (highest first)
    snippets = sorted(snippets, key=lambda x: x[1], reverse=True)
    
    return snippets

def fact_check_with_openai(claim, snippets):
    """Use OpenAI API to fact-check the claim with relevant snippets."""
    prompt = (
        "You are an expert fact-checker. Use the following relevant information to fact-check the claim:\n\n"
        "Claim: {claim}\n\n"
        "Relevant Information:\n\n"
    )
    relevant_info = "\n\n".join([f"({i+1}) {snippet[0]}" for i, snippet in enumerate(snippets)])
    prompt = prompt.format(claim=claim) + relevant_info

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


# Main process
async def main():
    # Example trusted sources (in practice, use a database or files)
    trusted_sources = {
    "source_1": (
        "The earth revolves around the sun in an elliptical orbit, as described by Kepler's laws of planetary motion. "
        "Kepler's first law states that the orbit of a planet around the sun is an ellipse, with the sun at one of the foci. "
        "This phenomenon is explained by gravitational forces and inertia, as elaborated by Newton's laws of motion. "
        "The elliptical orbit causes variations in the Earth's distance from the sun throughout the year, leading to "
        "seasonal differences in solar energy received by the planet. It is important to note that while the orbit is "
        "elliptical, it is nearly circular, with an eccentricity close to 0."
    ),
    "source_2": (
        "Water exhibits interesting phase transitions under different environmental conditions. At sea level, water boils "
        "at 100 degrees Celsius and freezes at 0 degrees Celsius. However, these temperatures vary with atmospheric pressure. "
        "At higher altitudes, where atmospheric pressure is lower, the boiling point decreases significantly, and water may "
        "boil at temperatures as low as 80 degrees Celsius. Freezing points can also shift slightly depending on impurities "
        "in the water or external pressure. The unique properties of water make it essential for life and a key substance in "
        "many natural processes, such as the water cycle, where evaporation, condensation, and precipitation regulate Earth's climate."
    ),
    "source_3": (
        "Paris, the capital of France, is renowned for its cultural and historical landmarks. The Eiffel Tower, built for the "
        "1889 World's Fair, remains a symbol of French ingenuity. The Louvre Museum houses thousands of art pieces, including "
        "Leonardo da Vinci's Mona Lisa. Paris has also been a hub for intellectual and political movements, influencing Europe "
        "and the world for centuries. The city's architecture, art, cuisine, and fashion continue to attract millions of tourists annually."
    ),
}

    
    # Example user_id (in a real-world scenario, this would be dynamically generated or provided)
    user_id = 1244  # Example for testing
    
    # Add trusted sources to Pinecone for the user
    await add_sources_to_pinecone(user_id, trusted_sources)
    
    # Retrieve sources relevant to the claim for the user
    user_claim = "The earth revolves around the sun in a circular orbit."
    
    # Precompute claim embedding once for later use
    claim_embedding = embed_text(user_claim)
    
    relevant_sources = retrieve_sources_from_pinecone(user_id, user_claim, precomputed_claim_embedding=claim_embedding)
    
    # Extract the most relevant snippets
    snippets = extract_relevant_snippets(user_claim, relevant_sources, claim_embedding)
    
    # Perform fact-checking using the relevant snippets
    fact_check_result = fact_check_with_openai(user_claim, snippets)
    
    # Output the result
    print("Claim:", user_claim)
    print("Relevant Snippets:", snippets)
    print("Fact-Check Result:", fact_check_result)

if __name__ == "__main__":
    asyncio.run(main())
