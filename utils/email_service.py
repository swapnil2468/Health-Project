import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class EmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS', 'noreply@medicalcenter.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', 'your_app_password_here')
        
        # Check if real email credentials are provided
        self.mock_mode = not all([self.email_address != 'noreply@medicalcenter.com', self.email_password != 'your_app_password_here'])
    
    def send_email(self, to_email, subject, body):
        """Send a simple text email"""
        try:
            if self.mock_mode:
                print(f"[MOCK EMAIL] To: {to_email}")
                print(f"[MOCK EMAIL] Subject: {subject}")
                print(f"[MOCK EMAIL] Body: {body[:100]}...")
                return True
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.email_address, self.email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_email_with_attachment(self, to_email, subject, body, attachment_path):
        """Send email with attachment"""
        try:
            if self.mock_mode:
                print(f"[MOCK EMAIL WITH ATTACHMENT] To: {to_email}")
                print(f"[MOCK EMAIL WITH ATTACHMENT] Subject: {subject}")
                print(f"[MOCK EMAIL WITH ATTACHMENT] Attachment: {attachment_path}")
                print(f"[MOCK EMAIL WITH ATTACHMENT] Body: {body[:100]}...")
                return True
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment if file exists
            if os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    # Create MIMEBase object
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                # Encode file in ASCII characters to send by email    
                encoders.encode_base64(part)
                
                # Add header as key/value pair to attachment part
                filename = os.path.basename(attachment_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}',
                )
                
                # Attach the part to message
                msg.attach(part)
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.email_address, self.email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            print(f"Email with attachment sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email with attachment: {e}")
            return False
    
    def send_html_email(self, to_email, subject, html_body):
        """Send HTML formatted email"""
        try:
            if self.mock_mode:
                print(f"[MOCK HTML EMAIL] To: {to_email}")
                print(f"[MOCK HTML EMAIL] Subject: {subject}")
                print(f"[MOCK HTML EMAIL] HTML Body: {html_body[:100]}...")
                return True
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Create HTML part
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.email_address, self.email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            print(f"HTML email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending HTML email: {e}")
            return False
