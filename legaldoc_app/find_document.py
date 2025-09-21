import os
from google.adk.tools import FunctionTool

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")

def find_document_by_name(name: str) -> str:
  """
  Finds a document by its name.

  Args:
    name: The name of the document to find.

  Returns:
    The document content as a string, or an error message if not found.
  """
  try:
    file_path = os.path.join(DOCUMENTS_DIR, name)
    if os.path.exists(file_path):
      with open(file_path, "r") as f:
        return f.read()
    else:
      return f"Document with name '{name}' not found."
  except Exception as e:
    return f"Error while finding document: {e}"

find_document_by_name_tool = FunctionTool(func=find_document_by_name)
