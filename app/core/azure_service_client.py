from openai import AzureOpenAI
from app.core.config.config import Config
 
class AzureOpenAIClient:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
 
    def generate_embedding(self, text: str):
        response = self.client.embeddings.create(
            input=[text],
            model=Config.AZURE_OPENAI_EMBEDDING_MODEL_NAME
        )
        return response.data[0].embedding
 
    def generate_completion(self, prompt: str, max_tokens: int = 300):
        response = self.client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.1
        )
        return response.choices[0].message.content
