from llama_index.vector_stores import PineconeVectorStore
from llama_index import VectorStoreIndex, SimpleKeywordTableIndex

# Set up PineconeVectorStore
vector_store = PineconeVectorStore(pinecone_index=index, embedding_model=embedding_model)

# Initialize LlamaIndex with Pinecone
index = VectorStoreIndex.from_documents(
    documents=[
        {"id": "1", "text": "Sample text for indexing."},
        {"id": "2", "text": "Another piece of content."}
    ],
    vector_store=vector_store,
    embedding_model=embedding_model,
)
