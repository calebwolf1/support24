import pinecone
from dotenv import load_dotenv


# initialize Pinecone
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"))

# Define the vector database
index_name = "llama-index"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, dimension=1536)  # Dimension depends on your embedding model

index = pinecone.Index(index_name)