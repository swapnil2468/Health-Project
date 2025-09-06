import os
from twilio.rest import Client

class SMSService:
    """Service for sending SMS messages via Twilio"""
    
    def __init__(self):
        # Twilio configuration from environment variables
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # For development/testing, we'll use mock sending if credentials not provided
        self.mock_mode = not all([self.account_sid, self.auth_token, self.twilio_phone_number])
        
        if not self.mock_mode:
            self.client = Client(self.account_sid, self.auth_token)
    
    def send_sms(self, phone_number, message):
        """Send SMS message to the specified phone number"""
        try:
            if self.mock_mode:
                print(f"[MOCK SMS] To: {phone_number}")
                print(f"[MOCK SMS] Message: {message}")
                return True
            
            # Clean and format phone number for Indian numbers
            clean_number = phone_number.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            
            # Handle Indian phone numbers (+91)
            if not clean_number.startswith('+'):
                if clean_number.startswith('91') and len(clean_number) == 12:
                    phone_number = f'+{clean_number}'
                elif len(clean_number) == 10:
                    phone_number = f'+91{clean_number}'
                else:
                    phone_number = f'+91{clean_number}'
            else:
                phone_number = clean_number
            
            # Send SMS via Twilio
            message = self.client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=phone_number
            )
            
            print(f"SMS sent successfully to {phone_number}. Message SID: {message.sid}")
            return True
            
        except Exception as e:
            print(f"Error sending SMS to {phone_number}: {e}")
            return False
    
    def send_bulk_sms(self, phone_numbers, message):
        """Send SMS to multiple phone numbers"""
        results = []
        
        for phone_number in phone_numbers:
            result = self.send_sms(phone_number, message)
            results.append({
                'phone_number': phone_number,
                'success': result
            })
        
        return results
    
    def validate_phone_number(self, phone_number):
        """Validate phone number format for Indian numbers"""
        import re
        
        # Remove all non-digit characters
        clean_number = re.sub(r'\D', '', phone_number)
        
        # Check if it's a valid Indian phone number
        if len(clean_number) == 10:
            return f'+91{clean_number}'
        elif len(clean_number) == 12 and clean_number.startswith('91'):
            return f'+{clean_number}'
        elif len(clean_number) == 13 and clean_number.startswith('91'):
            return f'+{clean_number[:12]}'
        else:
            return None
    
    def format_phone_for_display(self, phone_number):
        """Format phone number for display in Indian format"""
        import re
        
        # Remove all non-digit characters
        clean_number = re.sub(r'\D', '', phone_number)
        
        if len(clean_number) >= 10:
            # Handle Indian phone numbers
            if clean_number.startswith('91'):
                # Remove country code for formatting
                number_part = clean_number[2:]
                if len(number_part) == 10:
                    return f'+91 - {number_part[:5]} {number_part[5:]}'
            elif len(clean_number) == 10:
                return f'+91 - {clean_number[:5]} {clean_number[5:]}'
        
        return phone_number
