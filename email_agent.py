from ollama import chat
from IPython.display import Markdown,display
from email_extractor import email_fetch


def summarize_email():
    email_messages = email_fetch(count=3)
    response = chat(
    model = "gemma2:9b",
    messages = [{'role':'system','content':'You are email summarization assistant,You will get emails and your task is to summarize it following this rules:\n.Do not add information from your own\nIf the emails lacks information do not complete them by yourself present it as it is\n.Do not miss any important point on the emails provided' },
                {'role':'user','content':email_messages}]
    )
    return response.message.content

def display_summary():
    summary = summarize_email()
    display(Markdown(summary))

display_summary()

