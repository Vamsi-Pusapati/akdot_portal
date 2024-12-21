import os
from pymongo import MongoClient
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import Client
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SubscribeService():
    def __init__(self) -> None:
        self.mongoUrl = os.environ.get("MONGO_URL")
        self.client = MongoClient(self.mongoUrl)
        

    def put_subscribe_data (self, data):
        db = self.client.akdot
        collection = db.subscribe

        # Insert data into the collection
        inserted_id = collection.insert_one(data).inserted_id

        return inserted_id
    
    



    def send_email(self, subject, message, to_addr, name,from_addr='yhemanthsai555@gmail.com', password='your_password'):
        try:
            print("in send email")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_addr, password)
            
            # Create the email message as HTML
            email_message = MIMEMultipart("alternative")
            email_message['From'] = from_addr
            email_message['To'] = to_addr
            email_message['Subject'] = subject
            email_message.add_header('Reply-To', 'unsubscribe@akdot.com')
            
            # HTML Message
            html_message = f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            margin: 0;
                            padding: 0;
                            background-color: #FAFAFA;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 20px auto;
                            padding: 20px;
                            background-color: #FFFFFF;
                            border-radius: 10px;
                            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        }}
                        .header {{
                            background-color: #0056b3;
                            color: #FFFFFF;
                            padding: 10px 20px;
                            text-align: center;
                            border-radius: 10px 10px 0 0;
                            border-bottom: 4px solid #004494;
                        }}
                        .header img {{
                            height: 50px;
                            /* Adjust logo height as needed */
                        }}
                        .content {{
                            padding: 20px;
                            text-align: left;
                            line-height: 1.5;
                            border-bottom: 1px solid #EEE;
                        }}
                        .signature {{
                            padding: 20px;
                            text-align: left;
                            font-size: 0.9em;
                            color: #555;
                        }}
                        .unsubscribe {{
                            font-size: 0.8em;
                            text-align: center;
                            margin-top: 10px;
                        }}
                        .unsubscribe a {{
                            color: #0056b3;
                            text-decoration: none;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <!-- Adjust the 'src' to your logo image URL -->
                            <h2>Port of Alaska Notification Service</h2>
                        </div>
                        <div class="content">
                            <p>Dear {name},</p>
                            </br>
                            <p>This email confirms that you have successfully subscribed to Port of Alaska alerts service. You will now receive important notifications and updates regarding port operations, weather advisories, and other pertinent information directly to your inbox.</p>
                            </br>
                            <p> Thank you for subscribing and staying connected with us. Should you have any questions or concerns, please don't hesitate to contact us at <a href="mailto:portofalaska@anchorageak.gov">portofalaska@anchorageak.gov</a>.</p>
                        </div>
                        <div class="signature">
                            <p>Best Regards,</p>
                            <p>Port of Alaska Alerts Team</p>
                        </div>
                        <div class="unsubscribe">
                            <p>To unsubscribe from these notifications, please <a href="mailto:unsubscribe@anchorageak.gov?subject=Unsubscribe">click here</a>.</p>
                        </div>
                    </div>
                </body>
                </html>
                """

                # The rest of your send_email function follows...

            
            # Attach the HTML message
            email_message.attach(MIMEText(html_message, 'html'))
            
            # Send the email
            server.send_message(email_message)
            server.quit()
            print("Email sent successfully!")

        except Exception as e:
            print(f"Failed to send email: {e}")




    def send_textmessage(self, to, message = "Notification message from AKDoT"):
        try:
            
            # Your Twilio account SID and auth token
            account_sid = ''
            auth_token = ''
            client = Client(account_sid, auth_token)

            # Sending the SMS
            if not to.startswith("+1"):
                to = "+1" + to
            message = client.messages.create(
                to = to,  # Replace with the recipient's phone number
                from_ = "+18447143170",  # Replace with your Twilio phone number
                body = message
            )

            print(f"Message SID: {message.sid}")


        except Exception as e:
            print(f"Failed to send email: {e}")


