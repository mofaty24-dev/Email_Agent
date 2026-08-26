import os
from dotenv import load_dotenv
from imap_tools import MailBox, AND

# Loads EMAIL_ADDRESS and EMAIL_APP_PASSWORD from the .env file
# into environment variables, so we never hardcode secrets in code.
load_dotenv()

EMAIL = os.getenv('EMAIL_ADDRESS')
PASSWORD = os.getenv('EMAIL_PASSCODE')

# Gmail's IMAP server address — Outlook would use 'outlook.office365.com' instead.
IMAP_SERVER = 'imap.gmail.com'


def email_fetch(count=3):
    with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD) as mailbox:
        messages = list(mailbox.fetch(AND(all=True), limit=count, reverse=True))

        combined_text = ''
        for msg in messages:
            # Build a clear block per message so the LLM (or whatever consumes
            # this later) can tell where one email ends and the next begins.
            combined_text += f"From: {msg.from_}\n"
            combined_text += f"Subject: {msg.subject}\n"
            combined_text += f"Date: {msg.date}\n"
            combined_text += f"Body:\n{msg.text if msg.text else '(no plain text body)'}\n"
            combined_text += '\n' + ('=' * 50) + '\n\n'  # separator between emails

        return combined_text


if __name__ == '__main__':
    all_emails_text = email_fetch(count=3)
    print(all_emails_text)

