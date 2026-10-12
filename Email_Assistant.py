from imaplib import IMAP4_SSL
import imaplib
import smtplib
from email.message import EmailMessage
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import (HumanInTheLoopMiddleware,wrap_model_call,ModelResponse,ModelRequest,dynamic_prompt)
from dataclasses import dataclass
import os
from email import message_from_bytes
from email.header import decode_header
from dotenv import load_dotenv
from typing import Callable
from langgraph.types import Command
from langchain.messages import ToolMessage
from models import groq_model


load_dotenv()

# make a class with dataset to keep the password and email address
@dataclass
class Email_Context:
    email_address: str = "mofaty24@gmail.com"
    password: str = "123456"

# make class with authentication state to be edited through human-agent conversation
class AuthenticationState(AgentState):
    authenticated: bool

# make tools to read, search , send emails and authenticate the user
email_address = os.environ["EMAIL_ADDRESS"]
email_password = os.environ["EMAIL_PASSCODE"]

@tool
def search_emails(
    sender:str=None,
    subject:str=None,
    since=None,
    unread:bool=False,
    limit:int =10
):
    """
    Search Gmail inbox by sender, subject, date, or unread status, you can specify number of emails to return with limit parameter.

    since: Date formatted as DD-Mon-YYYY, e.g. 01-Oct-2026
    """



    if not email_address or not email_password:
        raise ValueError("Missing email credentials.")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    try:
        mail.login(email_address, email_password)
        mail.select("INBOX", readonly=True)

        criteria = []

        if sender:
            criteria.extend(["FROM", f'"{sender}"'])

        if subject:
            criteria.extend(["SUBJECT", f'"{subject}"'])

        if since:
            criteria.extend(["SINCE", since])

        if unread:
            criteria.append("UNSEEN")

        if not criteria:
            criteria = ["ALL"]

        status, data = mail.search(None, *criteria)

        if status != "OK":
            return {"error": "Email search failed."}

        email_ids = data[0].split()
        email_ids = email_ids[-limit:]  # Most recent matching IDs

        results = []

        for email_id in reversed(email_ids):
            status, data = mail.fetch(email_id, "(BODY.PEEK[HEADER])")

            if status != "OK" or not data or not isinstance(data[0], tuple):
                continue

            msg = message_from_bytes(data[0][1])

            def decode_header_value(value):
                parts = decode_header(value or "")
                decoded = ""

                for part, encoding in parts:
                    if isinstance(part, bytes):
                        decoded += part.decode(encoding or "utf-8", errors="replace")
                    else:
                        decoded += part

                return decoded

            results.append({
                "id": email_id.decode(),
                "from": decode_header_value(msg.get("From")),
                "subject": decode_header_value(msg.get("Subject")),
                "date": msg.get("Date")
            })

        return results

    finally:
        try:
            mail.logout()
        except Exception as e:
            print(f"Error logging out: {e}")

@tool
def send_email(to_email: str, subject: str, body: str) -> bool:
    """ Send an email to a specified recipient with a subject and body. Returns True if successful, False otherwise. """
    if not email_address or not email_password:
        raise ValueError("Missing EMAIL_ADDRESS or EMAIL_PASSWORD.")
    msg = EmailMessage()
    msg["From"] =email_address
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
            return True
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
        return False

# Example success = send_email( to_email="recipient@example.com", subject="Meeting Reminder", body="Hello, this is a reminder about our meeting tomorrow." ) print("Email sent successfully!" if success else "Email sending failed.")

@tool
def authenticate(email: str, password: str,runtime:ToolRuntime[Email_Context]):
    """ Authenticate the user by checking the provided email and password against stored credentials. Returns True if authenticated, False otherwise. """
    if email == runtime.context.email_address and password == runtime.context.password:
        return  Command(
            update={
                "authenticated": True,
                "messages": [
                    ToolMessage("Successfully authenticated", tool_call_id=runtime.tool_call_id)
                ],
            }
        )
    else:
        return Command(
            update={
                "authenticated": False,
                "messages": [
                    ToolMessage("Authentication failed. Please check your email and password.", tool_call_id=runtime.tool_call_id)
                ],
            }
        )


# make a middleware to give customer access to agent tools if he is authenticated
@wrap_model_call
async def dynamic_tool_call(request:ModelRequest,handler:Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    authenticated = request.state.get("authenticated")
    if authenticated:
       tools = [search_emails, send_email]
    else:
       tools = [authenticate]
    request = request.override(tools=tools)
    return await handler(request)

# make middleware to change agent system prompt based on the authentication state
@dynamic_prompt
def dynamic_prompt_func(request:ModelRequest) -> str:
    authenticated = request.state.get("authenticated")
    if authenticated:
        return "You are a helpful assistant that can search and send emails."
    else:
        return "You are a helpful assistant that can authenticate users, never search or send emails till user is authenticated."

# make the main agent with the tools and middlewares and a system prompt to ask for email and password to authenticate the user
agent = create_agent(
    model = groq_model,
    tools=[authenticate, search_emails, send_email],
    state_schema= AuthenticationState,
    context_schema= Email_Context,
    middleware=[dynamic_tool_call, dynamic_prompt_func,
                HumanInTheLoopMiddleware[AgentState,None](
                    interrupt_on= {"authenticate": False,
                                   "search_emails": False,
                                   "send_email": True},
                    description_prefix = "sending emails needs human approval."
                )],
)







