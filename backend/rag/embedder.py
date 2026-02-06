import os
from google import genai
from google.genai.errors import ClientError

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def embed(text: str):
    try:
        response = client.models.embed_content(
            model="models/text-embedding-004",
            contents=text,
        )
        return response.embeddings[0].values
    except ClientError as e:
        print(f"Error embedding text: {e}")
        return []
