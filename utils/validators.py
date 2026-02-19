import re

def validate_email(email):
    """
    Validate email format using regex.
    Returns True if valid, False otherwise.
    """
    if not email:
        return False
    # Standard email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """
    Validate phone number (10 digits).
    Returns True if valid, False otherwise.
    """
    if not phone:
        return False
    # 10 digit number
    pattern = r'^\d{10}$'
    return bool(re.match(pattern, phone))

def validate_pincode(pincode):
    """
    Validate pincode (6 digits).
    Returns True if valid, False otherwise.
    """
    if not pincode:
        return False
    # 6 digit number
    pattern = r'^\d{6}$'
    return bool(re.match(pattern, pincode))


def validate_password(password):
    """
    Validate password strength:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if not password or len(password) < 8:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[a-z]', password):
        return False
        
    if not re.search(r'\d', password):
        return False
        
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
        
    return True
