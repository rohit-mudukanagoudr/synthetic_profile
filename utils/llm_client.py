"""
Import necessary libraries
"""

import os
import sys
sys.path.append('./')
from openai import AzureOpenAI
from utils.log_utils import logger
from dotenv import load_dotenv
load_dotenv('env.env')

OPENAI_API_KEY = os.getenv('GPT4_KEY')
DEPLOYMENT = os.getenv('DEPLOYMENT_V4')
OPENAI_API_VERSION = os.getenv('API_VERSION')
SERVICE_LINE = os.getenv('SERVICE_LINE')
BRAND = os.getenv('BRAND')
PROJECT = os.getenv('PROJECT')
AZURE_OPENAI_ENDPOINT = os.getenv('END_POINT')
  
client = AzureOpenAI(
  #base_url= os.getenv("BASE_URL"),
  api_key = OPENAI_API_KEY, 
  api_version = OPENAI_API_VERSION,
  azure_endpoint = AZURE_OPENAI_ENDPOINT,
  azure_deployment = DEPLOYMENT,
  default_headers= {
    # Request headers
    'x-service-line': SERVICE_LINE,
    'x-brand': BRAND,
    'x-project': PROJECT,
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    'api-version': 'v15',
    'Ocp-Apim-Subscription-Key': OPENAI_API_KEY,
    }
)

def get_completion(prompt):
    try:
        # history_processed = str(history)
        logger.info("LLM CLIENT: Sending request with %s", prompt)
        messages = [{"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model = 'gpt-4-turbo-128k', #DEPLOYMENT,
            messages = messages,
            temperature=0,
        )

        logger.info("LLM CLIENT: Successfully generated the response: %s", response.choices[0].message.content)
        return response.choices[0].message.content
    
    except Exception as err:
        logger.error("LLM CLIENT: Could not generate response %s", err)
        return None



# print(get_completion("What is my name"))