import base64
from email.mime.text import MIMEText
from requests import HTTPError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scope of the API access
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Create the flow object and start the authorization process
flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
credentials = flow.run_local_server(port=0)

# Use the credentials to create a Gmail API client
service = build('gmail', 'v1', credentials=credentials)
message = MIMEText('Hi This is your account activation')
message['to'] = 'shazflicks@gmail.com'
message['subject'] = 'NEXPAY: Account Activation User Account'

# Define the message to be sent
create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

try:
    message = (service.users().messages().send(userId="me", body=create_message).execute())
    print(F'sent message to {message} Message Id: {message["id"]}')
except HTTPError as error:
    print(F'An HTTP error occurred: {error}')
    message = None

