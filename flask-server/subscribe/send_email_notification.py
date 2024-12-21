import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, message, to_addr, from_addr='yhemanthsai555@gmail.com', password='Opentext5*'):
    try:
        # Set up the email server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_addr, password)
        
        # Create the email message
        email_message = MIMEMultipart()
        email_message['From'] = from_addr
        email_message['To'] = to_addr
        email_message['Subject'] = subject
        email_message.attach(MIMEText(message, 'plain'))
        
        # Send the email
        server.send_message(email_message)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage
send_email(
    subject="Test Email",
    message="This is a test email from Python.",
    to_addr="yhemanthsai555@gmail.com",
    from_addr="yhemanthsai555@gmail.com",
    password=""
)
