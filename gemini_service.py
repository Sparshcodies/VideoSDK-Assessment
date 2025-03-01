# gemini_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Initialize the Gemini client (google-genai uses pydantic 2.x)
client = genai.Client(api_key=os.getenv("LLM_API_KEY"))

class GenerateRequest(BaseModel):
    user_input: str
    # Optionally, add image_data or other fields if needed

@app.post("/generate")
async def generate_text(req: GenerateRequest):
    system_instruction = (
        "You are a helpful assistant named \'Bucky\'. Respond in one or two short lines only. "
        "Do not elaborate unless explicitly asked for more details. Do not respond if there's only \'you\' in the text."
        "Do not reply if the request doesn't seem like a request or a question, just say \'...\' only   "
        )
    try:
        stream = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=req.user_input,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=50
            )
        )
        response_text = ""
        for chunk in stream:
            response_text += chunk.text
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
