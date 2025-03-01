from typing import Optional
import requests
from tts.tts import TTS
from intelligence.intelligence import Intelligence

class GeminiIntelligence(Intelligence):
    def __init__(self, api_url: str, tts: TTS, system_prompt: str):
        self.api_url = api_url
        self.tts = tts
        self.system_prompt = system_prompt
        self.chat_history = []
        self.pubsub = None
    
    def set_pubsub(self, pubsub):
        self.pubsub = pubsub
    
    def build_messages(self, text: str, sender_name: str):
        # Build the message
        human_message = {
            "role": "user",
            "type": "human",
            "name": sender_name.replace(" ", "_"),
            "content": text,
        }

        # Add message to history
        self.chat_history.append(human_message)
        
        # Note: The Gemini service as implemented doesn't use chat history
        # It simply takes the current user input
        return text

    def add_response(self, text):
        ai_message = {
            "role": "assistant",
            "type": "ai",
            "name": "Bucky",
            "content": text,
        }

        self.chat_history.append(ai_message)

    def generate(self, text: str, sender_name: str):
        # Build the message using history and context
        message = self.build_messages(text, sender_name=sender_name)
        
        # Call the Gemini microservice
        try:
            response = requests.post(
                self.api_url,
                json={"user_input": message},
                timeout=10
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                response_text = response.json().get("response", "")
                
                # Generate text using TTS
                self.tts.generate(text=response_text)
                
                print(f"[Interviewer]: {response_text}")
                if self.pubsub is not None:
                    # publish in meeting
                    self.pubsub(message=f"[Interviewer]: {response_text}")
                
                # add response to history
                self.add_response(response_text)
            else:
                error_message = f"Error calling Gemini service: {response.status_code} - {response.text}"
                print(error_message)
                # Could add fallback behavior here
                
        except Exception as e:
            print(f"Exception while calling Gemini service: {str(e)}")
            # Could add fallback behavior here