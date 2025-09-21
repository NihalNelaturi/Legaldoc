import os
from google.adk.tools import FunctionTool

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")

def delete_document(title: str) -> str:
  """
  Deletes a document.

  Args:
    title: The title of the document to be deleted.

  Returns:
    A message indicating the result of the operation.
  """
  try:
    file_path = os.path.join(DOCUMENTS_DIR, title)
    if os.path.exists(file_path):
      os.remove(file_path)
      return f"Document with title '{title}' has been deleted."
    else:
      return f"Document with title '{title}' not found."
  except Exception as e:
    return f"Error while deleting document: {e}"

delete_document_tool = FunctionTool(func=delete_document)
