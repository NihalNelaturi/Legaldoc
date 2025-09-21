import os
from google.adk.tools import FunctionTool

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")

def list_documents() -> str:
  """
  Lists all the documents.

  Returns:
    A comma-separated list of all the document titles.
  """
  try:
    if not os.path.exists(DOCUMENTS_DIR):
      return "No documents found."
    documents = os.listdir(DOCUMENTS_DIR)
    if not documents:
      return "No documents found."
    return ", ".join(documents)
  except Exception as e:
    return f"Error while listing documents: {e}"

list_documents_tool = FunctionTool(func=list_documents)
