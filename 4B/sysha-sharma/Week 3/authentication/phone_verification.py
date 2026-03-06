# auth/phone_verification.py
from sqlalchemy.orm import Session
from database.state_tracking import get_or_create_user, get_or_create_active_conversation

def authenticate_phone_user(db: Session, phone_number: str, name: str = None):
    """
    Identifies a user by phone number across conversations.
    Creates a new user profile if they don't exist.
    """
    if not phone_number:
        raise ValueError("Phone number is required for authentication.")
    
    # Clean the phone number if needed (e.g., stripping '+' or spaces)
    cleaned_phone = phone_number.strip().replace("+", "")
    
    # Get or create the user in the database
    user = get_or_create_user(db=db, phone_number=cleaned_phone, name=name)
    
    # Ensure they have an active conversation context to identify them across messages
    conversation = get_or_create_active_conversation(db=db, user_id=user.id)
    
    return user, conversation