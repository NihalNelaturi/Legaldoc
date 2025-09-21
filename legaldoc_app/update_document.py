
import os
from google.adk.tools import FunctionTool

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")

def update_document(title: str, new_content: str) -> str:
  """
  Updates a document with new content.

  Args:
    title: The title of the document to be updated.
    new_content: The new content of the document.

  Returns:
    A message indicating the result of the operation.
  """
  try:
    file_path = os.path.join(DOCUMENTS_DIR, title)
    if os.path.exists(file_path):
      with open(file_path, "w") as f:
        f.write(new_content)
      return f"Document with title '{title}' has been updated."
    else:
      return f"Document with title '{title}' not found."
  except Exception as e:
    return f"Error while updating document: {e}"

update_document_tool = FunctionTool(func=update_document)
