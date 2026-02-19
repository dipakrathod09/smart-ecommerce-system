import random
import string
import re
from datetime import datetime

def format_currency(value):
    """Format value as currency (INR)"""
    if value is None:
        return "₹0.00"
    return "₹{:,.2f}".format(value)

def format_datetime(value, format='%d %b %Y, %I:%M %p'):
    """Format datetime object"""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format)

def truncate_text(text, length=100):
    """Truncate text to specified length"""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length] + '...'

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_random_string(length=10):
    """Generate a random alphanumeric string"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def slugify(text):
    """Create URL-friendly slug from text"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text
