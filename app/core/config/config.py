import os
from dotenv import load_dotenv

from pathlib import Path

env_path = Path(__file__).resolve().parent / "profiles" / ".env.dev"
load_dotenv(dotenv_path=env_path)
 

class Config:
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_EMBEDDING_MODEL_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL_NAME")
    AZURE_OPENAI_GPT_MODEL_NAME = os.getenv("AZURE_OPENAI_GPT_MODEL_NAME")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
    FORM_RECOGNIZER_API_KEY = os.getenv("FORM_RECOGNIZER_API_KEY")

    if not FORM_RECOGNIZER_ENDPOINT or not FORM_RECOGNIZER_API_KEY:
        raise ValueError("FORM_RECOGNIZER_ENDPOINT and FORM_RECOGNIZER_API_KEY must be set in the environment.")