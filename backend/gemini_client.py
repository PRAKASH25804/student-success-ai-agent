import os
import json
import logging
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment. Please add it to your .env file.")

def generate_json_response(prompt, system_instruction=None):
    """
    Calls Gemini 2.5 Flash and requests a JSON response.
    Has fallback to standard requests HTTP API if SDK fails.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")
    
    # Method 1: Using google-generativeai library
    try:
        model_name = 'gemini-2.5-flash'
        config = {
            "response_mime_type": "application/json"
        }
        
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=config,
                system_instruction=system_instruction
            )
        else:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=config
            )
            
        logger.info(f"Sending prompt to Gemini SDK... Prompt length: {len(prompt)}")
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        return json.loads(text)
        
    except Exception as e:
        logger.error(f"SDK Gemini call failed: {str(e)}. Attempting HTTP fallback...")
        
        # Method 2: HTTP Fallback using requests
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            
            if system_instruction:
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                    "generationConfig": {"responseMimeType": "application/json"}
                }
            else:
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
                
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            res_data = response.json()
            
            candidates = res_data.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "").strip()
                # Clean JSON wrapping (like ```json ... ```) if present in case of raw HTTP
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                return json.loads(text)
            else:
                raise ValueError(f"No response text in candidates: {res_data}")
                
        except Exception as http_err:
            logger.error(f"HTTP Fallback also failed: {str(http_err)}")
            raise http_err

def generate_text_response(prompt, system_instruction=None, history=None):
    """
    Calls Gemini 2.5 Flash for chat text generation (markdown supported).
    Allows history input.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")
        
    try:
        model_name = 'gemini-2.5-flash'
        
        if system_instruction:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction
            )
        else:
            model = genai.GenerativeModel(model_name=model_name)
            
        logger.info("Sending chat/text prompt to Gemini SDK...")
        
        if history:
            formatted_history = []
            for h in history:
                # Ensure role maps to user/model
                role = "user" if h["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [{"text": h["content"]}]})
            
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(prompt)
        else:
            response = model.generate_content(prompt)
            
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"SDK Text generation failed: {str(e)}. Attempting HTTP fallback...")
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            
            formatted_contents = []
            if history:
                for h in history:
                    formatted_contents.append({
                        "role": "user" if h["role"] == "user" else "model",
                        "parts": [{"text": h["content"]}]
                    })
            
            formatted_contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })
            
            payload = {
                "contents": formatted_contents
            }
            if system_instruction:
                payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
                
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            res_data = response.json()
            
            candidates = res_data.get("candidates", [])
            if candidates:
                return candidates[0].get("content", {}).get("parts", [])[0].get("text", "").strip()
            else:
                raise ValueError(f"No response text in candidates: {res_data}")
        except Exception as http_err:
            logger.error(f"HTTP text fallback failed: {str(http_err)}")
            raise http_err
