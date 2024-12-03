# from llama_index.vector_stores.pinecone import PineconeVectorStore
# from llama_index.core import VectorStoreIndex, Document
# from pinecone import Pinecone, ServerlessSpec
# from pinecone.grpc import PineconeGRPC
# import openai
# import dotenv
# import os
# import asyncio
# import nest_asyncio
# nest_asyncio.apply()

# dotenv.load_dotenv()

# # Initialize Pinecone
# pc = PineconeGRPC(api_key=os.getenv("PINECONE_API_KEY"))
# index_name = "sources"

# # Create index here (skip step if index already initialized)
# # pc.create_index(
# #     index_name,
# #     dimension=1536,
# #     spec=ServerlessSpec(cloud="aws", region="us-east-1"),
# # )

# # Initialize Index and VectorStore
# pc_index = pc.Index(index_name)
# vector_store = PineconeVectorStore(index_name=index_name, client=pc)

# # Initialize OpenAI API Key
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # Define initial pipeline
# pipeline -


# def embed_text(text):
#     response = openai.embeddings.create(
#         model="text-embedding-ada-002",
#         input=[text]
#     )
#     return response.data[0].embedding  # Accessing the embedding from the response

# # Create a Pinecone Vector Store for LlamaIndex
# def create_pinecone_vector_store():
#     return PineconeVectorStore(index_name=index_name, client=pc)

# # Add sources to Pinecone and LlamaIndex
# async def add_sources_to_pinecone(user_id, sources):
#     """Embed and store trusted sources in Pinecone for a specific user."""
#     namespace = f"user_{user_id}"
#     for source_id, content in sources.items():
#         embedding = embed_text(content)
#         pc.Index(index_name).upsert([(source_id, embedding, {"content": content})], namespace=namespace)
    
#     # Wait to ensure data is indexed before querying
#     await wait_for_index_update(namespace)

# async def wait_for_index_update(namespace, retries=10, delay=2):
#     """Wait for Pinecone index to be updated."""
#     for _ in range(retries):
#         result = pc.Index(index_name).query(vector=[0] * 1536, top_k=1, namespace=namespace)
#         if result["matches"]:
#             return True
#         await asyncio.sleep(delay)

# # Create LlamaIndex using Pinecone as the vector store
# def create_index_from_sources(sources, vector_store):
#     documents = []
#     for source_id, content in sources.items():
#         documents.append(Document(text=content, doc_id=source_id))
    
#     # Create LlamaIndex using PineconeVectorStore as the underlying vector store
#     index = VectorStoreIndex.from_documents(documents, vector_store=vector_store)
#     return index

# # Retrieve sources from LlamaIndex (with Pinecone backend)
# async def retrieve_sources_with_llamaindex(user_claim, index):
#     """Retrieve relevant sources using LlamaIndex's cosine similarity."""
#     # Embed the user claim
#     claim_embedding = embed_text(user_claim)

#     # Initialize the SemanticSimilarityEvaluator with the index
#     evaluator = SemanticSimilarityEvaluator(index)
    
#     # Extract documents or embeddings from the index (assuming the index contains document vectors)
#     documents = await index.from_documents()  # or another method to retrieve documents or vectors
    
#     # Now, we need to create embeddings for the documents to use them as 'reference' 
#     # (assuming documents are text and need to be embedded)
#     document_embeddings = [embed_text(doc['text']) for doc in documents]
    
#     # Perform the semantic similarity search (response is the claim_embedding, reference is the document embeddings)
#     result = await evaluator.aevaluate(
#         response=claim_embedding,
#         reference=document_embeddings,
#     )
    
#     # Extract relevant sources based on the result (this depends on how your result is structured)
#     relevant_sources = result['sources']  # Adjust this part as per the actual structure of result
    
#     return [source['text'] for source in relevant_sources]



# async def main():
#     trusted_sources = {
#         "source_1": (
#             "The earth revolves around the sun in an elliptical orbit, as described by Kepler's laws of planetary motion. "
#             "Kepler's first law states that the orbit of a planet around the sun is an ellipse, with the sun at one of the foci. "
#             "This phenomenon is explained by gravitational forces and inertia, as elaborated by Newton's laws of motion. "
#             "The elliptical orbit causes variations in the Earth's distance from the sun throughout the year, leading to seasonal differences in solar energy received by the planet. "
#             "The Earth is closest to the sun during perihelion, which occurs in early January, and farthest from the sun during aphelion, which occurs in early July. "
#             "At perihelion, the Earth is about 147 million kilometers away from the sun, and at aphelion, it is about 152 million kilometers. "
#             "This variation in distance is minimal, but it does contribute to small seasonal differences. Although this change in distance affects the amount of solar radiation reaching the Earth, it is the tilt of the Earth's axis that is the main driver of seasonal temperature changes. "
#             "Kepler's second law, or the law of areas, explains that planets move faster when they are closer to the sun and slower when they are farther away. "
#             "This is due to the conservation of angular momentum, and the change in speed of the Earth's motion contributes to the length of different seasons. "
#             "Kepler's third law, the law of harmonies, relates the length of time a planet takes to orbit the sun to its average distance from the sun. "
#             "In our case, the Earth's orbital period is approximately 365.25 days, and this period is consistent over time, allowing the seasons to be predictable year after year. "
#             "The Earth's orbit, while elliptical, is very close to circular, with an eccentricity of only about 0.0167, making it one of the least elliptical planetary orbits in the solar system. "
#             "This slight eccentricity is why we experience seasonal variations in temperature, but not extreme shifts in climate. "
#             "In fact, the variation in Earth's distance from the sun is not the main cause of the seasons — it is the axial tilt of the Earth (approximately 23.5 degrees) that is the primary factor in creating seasonal temperature changes."
#         ),
#         "source_2": (
#             "The process of photosynthesis is essential to life on Earth, as it enables plants, algae, and certain bacteria to convert solar energy into chemical energy. "
#             "In plants, this process occurs in the chloroplasts, where sunlight is absorbed by chlorophyll, a green pigment that plays a crucial role in capturing light. "
#             "During photosynthesis, plants take in carbon dioxide from the air and water from the soil, producing glucose and oxygen as byproducts. "
#             "The glucose provides energy for the plant's growth and development, while the oxygen is released into the atmosphere, which is vital for maintaining life on Earth. "
#             "In addition to chlorophyll, plants also contain other pigments such as carotenoids and phycobilins that help absorb light and protect against damage caused by excessive sunlight. "
#             "The overall equation for photosynthesis can be expressed as: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2. "
#             "This process not only sustains plant life but is also the foundation of the food chain, as animals and humans rely on plants as a primary source of food and oxygen. "
#             "Without photosynthesis, the Earth's atmosphere would lack the oxygen required by aerobic organisms, and the energy stored in glucose would not be available for the growth of other organisms. "
#             "In addition to its importance for life on Earth, photosynthesis also plays a key role in the carbon cycle, helping to regulate atmospheric carbon dioxide levels and mitigate climate change. "
#             "Plants absorb large amounts of carbon dioxide during photosynthesis, and by removing this greenhouse gas from the atmosphere, they help reduce the effects of global warming. "
#             "Photosynthesis also supports the production of biomass, which is crucial for food production, wood, and other agricultural products that sustain human society. "
#             "In addition to plants, some algae and bacteria perform photosynthesis, contributing to oxygen production in marine and freshwater ecosystems."
#         ),
#         "source_3": (
#             "The human brain is a highly complex and dynamic organ, responsible for controlling every aspect of our body, from basic functions like breathing and heart rate to complex processes like thought, memory, and emotion. "
#             "It is made up of approximately 86 billion neurons, each connected to thousands of other neurons through synapses, forming intricate neural networks that allow for communication between different regions of the brain. "
#             "These neural connections are constantly modified through a process called neuroplasticity, where the brain reorganizes itself in response to new experiences, learning, and even injury. "
#             "One of the most critical regions of the brain is the prefrontal cortex, which governs higher cognitive functions such as decision-making, problem-solving, and social behavior. "
#             "This part of the brain is essential for the control of impulses, planning, and understanding the consequences of actions, which makes it important in moral and ethical decision-making. "
#             "Recent research has shown that the brain continues to develop and change throughout our lives, with neuroplasticity occurring well into adulthood. "
#             "The brain's ability to rewire itself after injury is particularly significant in rehabilitation after strokes, head trauma, and other neurological disorders. "
#             "Understanding how the brain works has led to advancements in various fields, including neuroscience, psychology, and medicine, particularly in the treatment of neurological diseases like Alzheimer's and Parkinson's disease. "
#             "Technological advancements in brain imaging, such as MRI and PET scans, have allowed scientists to map brain activity in real-time, revealing how different areas of the brain are involved in tasks ranging from simple reflexes to complex cognitive activities. "
#             "Additionally, neuroimaging techniques are also being used to explore the roots of mental health disorders, including depression, schizophrenia, and anxiety, with the goal of developing more effective treatments."
#         ),
#     }
    
#     # Initialize Pinecone vector store for LlamaIndex
#     vector_store = create_pinecone_vector_store()
    
#     # Create a LlamaIndex index using Pinecone as the backend
#     index = create_index_from_sources(trusted_sources, vector_store)
    
#     # Claim to fact-check
#     user_claim = "The earth revolves around the sun in a circular orbit."
    
#     # Retrieve relevant sources from the LlamaIndex
#     relevant_sources = await retrieve_sources_with_llamaindex(user_claim, index)
    
#     # Output the relevant sources
#     print("Relevant Sources from LlamaIndex (with Pinecone):")
#     for source in relevant_sources:
#         print(source)

# if __name__ == "__main__":
#     asyncio.run(main())

from pinecone import Pinecone, ServerlessSpec
from llama_index.core import SimpleKeywordTableIndex, Document
import openai
import dotenv
import os
import asyncio
from sklearn.metrics.pairwise import cosine_similarity
from data_scrape import source_and_scrape
import time
import json

dotenv.load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment="us-east-1")
index_name = "sources"
pc.delete_index(index_name)

if not pc.has_index(index_name):
    pc.create_index(
        index_name,
        dimension=1536,
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

# Initialize Pinecone index
index = pc.Index(index_name)
# Instantiate the OpenAI client
openai_client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

def clear_index():
    pc.delete_index(index_name)

def embed_text(text):
    response = openai_client.embeddings.create(
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

    # Stores both the content of the source and its url (separated from the unique id necessary for 
    # storage of the chunks)
    return [(result["metadata"]["content"], result["id"].split("unique_number:")[0]) 
            for result in search_results["matches"]]

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

# function not needed anymore
def extract_relevant_snippets(claim, sources, claim_embedding=None, similarity_threshold=0.85):
    """
    Extract the most relevant snippets from sources based on cosine similarity.
    """
    if claim_embedding is None:
        claim_embedding = embed_text(claim)

    snippets = []
    for source in sources:
        # Chunk the source text into smaller segments
        # chunks = chunk_text(source, chunk_size=50, overlap=20)
        chunks = chunk_text(source[0], chunk_size=500, overlap=50)
        
        # Embed each chunk
        print("embedding chunks")
        chunk_embeddings = [embed_text(chunk) for chunk in chunks]
        print("finished embedding chunks")
        # Compute cosine similarity
        similarities = cosine_similarity([claim_embedding], chunk_embeddings)[0]
        
        # Filter chunks by similarity threshold
        relevant_chunks = [
            (chunks[i], similarities[i], source[1]) # stores source url as well for future use
            for i in range(len(chunks))
            if similarities[i] >= similarity_threshold
        ]
        
        # Add relevant chunks to the snippets list
        snippets.extend(relevant_chunks)
    
    # Sort snippets by similarity score (highest first)
    snippets = sorted(snippets, key=lambda x: x[1], reverse=True)
    
    return snippets

# fact-check the claim with relevant snippets using OpenAI LLM
def fact_check_with_openai(claim, snippets):
    """Use OpenAI API to fact-check the claim with relevant snippets."""
    prompt = (
        "You are an expert fact-checker. Use the following relevant information to fact-check the claim:\n\n"
        "Claim: {claim}\n\n"
        "Relevant Information:\n\n"
        "Output your response in JSON format with the factuality of the claim (true, false, or unknown), your confidence in this classification (0-100), and the context behind your decision. Example output:"
        "{{'factuality': 'true', 'confidence': 90, 'context': 'According to Google Finance, it is true that the stock price of NVIDIA is 138.25 USD. However, it is important to note that the stock price of NVIDIA does not reflect the status of the market as a whole. Though the price of NVIDIA increased, the market is still on the decline.'}}"
    )
    relevant_info = "\n\n".join([f"({i+1}) {snippet[0]}" for i, snippet in enumerate(snippets)])
    prompt = prompt.format(claim=claim) + relevant_info

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content # this line is prone to deprecation due to constant updates to openai API

# perform full fact checking pipeline on a given claim
async def fact_check(claim, user_id):
    api_key = os.getenv("GOOGLE_SEARCH_KEY")
    cx = os.getenv("SEARCH_ENGINE_ID")

    current_time = time.time() # for testing purposes
    # set up the web scraper to retrieve sources
    scraper = source_and_scrape.ClaimScraper(claim, api_key, cx)

    # builds a dictionary of url:content pairs from scraped sources
    sources = {}
    for entry in scraper.get_sources_and_scrape():
        count = 1
        for chunk in chunk_text(entry['content'], 1250, 20):
            id = f"{entry['url']}unique_number:{count}"
            sources[id] = chunk
            count += 1

    # Add sources to Pinecone for the user
    await add_sources_to_pinecone(user_id, sources)
    
    # Precompute claim embedding once for later use
    claim_embedding = embed_text(claim)
    
    # Extract relevant snippets from sources
    relevant_sources = retrieve_sources_from_pinecone(user_id, claim, precomputed_claim_embedding=claim_embedding)
    
    # Perform fact-checking using the relevant snippets
    fact_check_result = fact_check_with_openai(claim, relevant_sources)
    
    # Output the result
    print("Claim:", claim)
    print("Relevant Snippets:", relevant_sources)
    print("Fact-Check Result:", fact_check_result)
    print("time: ", time.time() - current_time)

    # Return json result of query
    result = json.loads(fact_check_result)
    result.update({"sources":list(set([snippet[1] for snippet in relevant_sources]))})
    print(result)
    return result

# main function to run the pipeline - TESTING PURPOSES ONLY
async def main():
    # Example trusted sources (in practice, use a database or files)
    trusted_sources = {
    "source_1": (
        "The earth revolves around the sun in an elliptical orbit, as described by Kepler's laws of planetary motion. "
        "Kepler's first law states that the orbit of a planet around the sun is an ellipse, with the sun at one of the foci. "
        "This phenomenon is explained by gravitational forces and inertia, as elaborated by Newton's laws of motion. "
        "The elliptical orbit causes variations in the Earth's distance from the sun throughout the year, leading to seasonal differences in solar energy received by the planet. "
        "The Earth is closest to the sun during perihelion, which occurs in early January, and farthest from the sun during aphelion, which occurs in early July. "
        "At perihelion, the Earth is about 147 million kilometers away from the sun, and at aphelion, it is about 152 million kilometers. "
        "This variation in distance is minimal, but it does contribute to small seasonal differences. Although this change in distance affects the amount of solar radiation reaching the Earth, it is the tilt of the Earth's axis that is the main driver of seasonal temperature changes. "
        "Kepler's second law, or the law of areas, explains that planets move faster when they are closer to the sun and slower when they are farther away. "
        "This is due to the conservation of angular momentum, and the change in speed of the Earth's motion contributes to the length of different seasons. "
        "Kepler's third law, the law of harmonies, relates the length of time a planet takes to orbit the sun to its average distance from the sun. "
        "In our case, the Earth's orbital period is approximately 365.25 days, and this period is consistent over time, allowing the seasons to be predictable year after year. "
        "The Earth's orbit, while elliptical, is very close to circular, with an eccentricity of only about 0.0167, making it one of the least elliptical planetary orbits in the solar system. "
        "This slight eccentricity is why we experience seasonal variations in temperature, but not extreme shifts in climate. "
        "In fact, the variation in Earth's distance from the sun is not the main cause of the seasons — it is the axial tilt of the Earth (approximately 23.5 degrees) that is the primary factor in creating seasonal temperature changes."
    ),
    "source_2": (
        "The process of photosynthesis is essential to life on Earth, as it enables plants, algae, and certain bacteria to convert solar energy into chemical energy. "
        "In plants, this process occurs in the chloroplasts, where sunlight is absorbed by chlorophyll, a green pigment that plays a crucial role in capturing light. "
        "During photosynthesis, plants take in carbon dioxide from the air and water from the soil, producing glucose and oxygen as byproducts. "
        "The glucose provides energy for the plant's growth and development, while the oxygen is released into the atmosphere, which is vital for maintaining life on Earth. "
        "In addition to chlorophyll, plants also contain other pigments such as carotenoids and phycobilins that help absorb light and protect against damage caused by excessive sunlight. "
        "The overall equation for photosynthesis can be expressed as: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2. "
        "This process not only sustains plant life but is also the foundation of the food chain, as animals and humans rely on plants as a primary source of food and oxygen. "
        "Without photosynthesis, the Earth's atmosphere would lack the oxygen required by aerobic organisms, and the energy stored in glucose would not be available for the growth of other organisms. "
        "In addition to its importance for life on Earth, photosynthesis also plays a key role in the carbon cycle, helping to regulate atmospheric carbon dioxide levels and mitigate climate change. "
        "Plants absorb large amounts of carbon dioxide during photosynthesis, and by removing this greenhouse gas from the atmosphere, they help reduce the effects of global warming. "
        "Photosynthesis also supports the production of biomass, which is crucial for food production, wood, and other agricultural products that sustain human society. "
        "In addition to plants, some algae and bacteria perform photosynthesis, contributing to oxygen production in marine and freshwater ecosystems."
    ),
    "source_3": (
        "The human brain is a highly complex and dynamic organ, responsible for controlling every aspect of our body, from basic functions like breathing and heart rate to complex processes like thought, memory, and emotion. "
        "It is made up of approximately 86 billion neurons, each connected to thousands of other neurons through synapses, forming intricate neural networks that allow for communication between different regions of the brain. "
        "These neural connections are constantly modified through a process called neuroplasticity, where the brain reorganizes itself in response to new experiences, learning, and even injury. "
        "One of the most critical regions of the brain is the prefrontal cortex, which governs higher cognitive functions such as decision-making, problem-solving, and social behavior. "
        "This part of the brain is essential for the control of impulses, planning, and understanding the consequences of actions, which makes it important in moral and ethical decision-making. "
        "Recent research has shown that the brain continues to develop and change throughout our lives, with neuroplasticity occurring well into adulthood. "
        "The brain's ability to rewire itself after injury is particularly significant in rehabilitation after strokes, head trauma, and other neurological disorders. "
        "Understanding how the brain works has led to advancements in various fields, including neuroscience, psychology, and medicine, particularly in the treatment of neurological diseases like Alzheimer's and Parkinson's disease. "
        "Technological advancements in brain imaging, such as MRI and PET scans, have allowed scientists to map brain activity in real-time, revealing how different areas of the brain are involved in tasks ranging from simple reflexes to complex cognitive activities. "
        "Additionally, neuroimaging techniques are also being used to explore the roots of mental health disorders, including depression, schizophrenia, and anxiety, with the goal of developing more effective treatments."
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
    # asyncio.run(main())
    # clear_index()
    asyncio.run(fact_check("Donald Trump considered inviting the Taliban to Camp David.", 1244))
