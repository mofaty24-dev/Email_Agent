import os
from dotenv import load_dotenv
from imap_tools import MailBox, AND


load_dotenv()

EMAIL = os.getenv('EMAIL_ADDRESS')
PASSWORD = os.getenv('EMAIL_PASSCODE')
IMAP_SERVER = 'imap.gmail.com'


def email_fetch(count=3):
    with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD) as mailbox:
        messages = list(mailbox.fetch(AND(all=True), limit=count, reverse=True))

        combined_text = ''
        for msg in messages:
            combined_text += f"From: {msg.from_}\n"
            combined_text += f"Subject: {msg.subject}\n"
            combined_text += f"Date: {msg.date}\n"
            combined_text += f"Body:\n{msg.text if msg.text else '(no plain text body)'}\n"
            combined_text += '\n' + ('=' * 50) + '\n\n'

        return combined_text