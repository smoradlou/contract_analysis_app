import os
from dotenv import load_dotenv
import pathlib


def load_config():
    env_file = pathlib.Path('.env')
    if env_file.exists():
        load_dotenv()

    return {
        'LLM_MODEL_NAME': os.getenv('LLM_MODEL_NAME'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    }