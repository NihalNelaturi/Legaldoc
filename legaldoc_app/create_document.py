
import os
from google.adk.tools import FunctionTool

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")

def create_document(title: str, content: str) -> str:
  """
  Creates a new document.

  Args:
    title: The title of the document.
    content: The content of the document.

  Returns:
    A message indicating the result of the operation.
  """
  try:
    if not os.path.exists(DOCUMENTS_DIR):
      os.makedirs(DOCUMENTS_DIR)
    file_path = os.path.join(DOCUMENTS_DIR, title)
    with open(file_path, "w") as f:
      f.write(content)
    return f"Document with title '{title}' has been created."
  except Exception as e:
    return f"Error while creating document: {e}"

create_document_tool = FunctionTool(func=create_document)
