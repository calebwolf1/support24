from llama_index.embeddings.openai import OpenAIEmbedding

# Use OpenAI's embeddings (or another supported model)
embedding_model = OpenAIEmbedding(model="text-embedding-ada-002", openai_api_key="YOUR_OPENAI_API_KEY")
