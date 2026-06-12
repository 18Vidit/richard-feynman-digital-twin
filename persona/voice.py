import os
import requests
import base64

def generate_feynman_audio(text: str) -> str:
    """
    Generates TTS audio using ElevenLabs API and returns a base64 encoded string.
    If the API key or Voice ID is missing, returns None.
    """
    from dotenv import load_dotenv
    env_path = r"c:\Users\ASUS\OneDrive\Desktop\digital twin project\.env"
    load_dotenv(env_path, override=True)
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    
    print(f"DEBUG: api_key loaded: {bool(api_key)}")
    print(f"DEBUG: voice_id loaded: {bool(voice_id)}")
    
    if not api_key or not voice_id:
        print("Missing API key or Voice ID!")
        return None
        
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            audio_bytes = response.content
            if not audio_bytes:
                raise Exception("ElevenLabs returned 200 OK but the audio data was EMPTY!")
            return base64.b64encode(audio_bytes).decode('utf-8')
        else:
            print(f"ElevenLabs API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error calling ElevenLabs: {e}")
        return None
