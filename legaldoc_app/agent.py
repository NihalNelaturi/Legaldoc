from google.adk.agents.llm_agent import Agent
from .summarizer import summarize_document_tool
from .update_document import update_document_tool
from .create_document import create_document_tool
from .find_document import find_document_by_name_tool
from .delete_document import delete_document_tool
from .list_documents import list_documents_tool
from .translate import translate_tool
from .text_to_speech import text_to_speech_tool
from .find_clause import find_clause_by_keyword_tool

tools = [
    summarize_document_tool,
    update_document_tool,
    create_document_tool,
    find_document_by_name_tool,
    delete_document_tool,
    list_documents_tool,
    translate_tool,
    text_to_speech_tool,
    find_clause_by_keyword_tool,
]

print("Loaded tools:", [tool.name for tool in tools])

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A helpful LEGALDOC assistant for user questions.",
    instruction="You are a legal document assistant. Your task is to help users with document-related functions like summarizing, creating, updating, or finding information. When summarizing a legal document, you should present the extracted information in a neutral and objective way. Do not provide legal advice.",
    tools=tools,
)
