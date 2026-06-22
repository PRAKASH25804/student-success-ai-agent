from backend.gemini_client import generate_text_response
from backend.db import get_chat_history, save_chat_message, get_profile

def chat_with_assistant(user_message, user_id=1):
    """
    Gets conversation history, user profile context, sends everything to Gemini 2.5 Flash,
    persists the messages, and returns the response.
    """
    if not user_message:
        raise ValueError("Message cannot be empty.")
        
    # Get user profile for context-aware counseling
    profile = get_profile(user_id)
    
    # Construct a helpful system instruction with student context
    system_instruction = (
        "You are 'SuccessAI', a friendly, positive, and deeply knowledgeable student success coach. "
        "Your mission is to help students with their academic planning, career counseling, resume adjustments, "
        "interview tips, skill gap remediation, and project suggestions. "
        f"You are speaking to {profile.get('name', 'Student')}, who wants to become a '{profile.get('career_goal', 'Professional')}' "
        f"and currently possesses skills in '{profile.get('skills', 'various domains')}'. "
        "Keep your advice highly practical, actionable, encouraging, and clear. "
        "Use bullet points, bold text, and markdown spacing where helpful to ensure high readability. "
        "Refer to their career goal and skills where appropriate, but remain open to any student-focused query."
    )
    
    # Retrieve past message history (last 10 messages to avoid context inflation/cost)
    raw_history = get_chat_history(user_id=user_id, limit=20)
    
    # Format history for Gemini SDK: list of {"role": "user"|"model", "content": "..."}
    formatted_history = []
    for chat in raw_history:
        formatted_history.append({
            "role": "user" if chat["sender"] == "user" else "model",
            "content": chat["message"]
        })
        
    # Run the query through Gemini
    response_text = generate_text_response(
        prompt=user_message,
        system_instruction=system_instruction,
        history=formatted_history
    )
    
    # Save user message and model response to SQLite
    save_chat_message(user_id=user_id, sender="user", message=user_message)
    save_chat_message(user_id=user_id, sender="assistant", message=response_text)
    
    return response_text
