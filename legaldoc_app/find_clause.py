import re
from google.adk.tools import FunctionTool

def find_clause_by_keyword(document: str, keyword: str) -> str:
  """
  Finds a specific clause in a document based on a keyword.

  Args:
    document: The document to search in.
    keyword: The keyword to search for (e.g., "Limitation of Liability").

  Returns:
    The text of the clause containing the keyword, or an error message if not found.
  """
  # Split the document into paragraphs
  paragraphs = document.split('\n\n')
  
  for p in paragraphs:
    if re.search(r'\b' + keyword + r'\b', p, re.IGNORECASE):
      return p.strip()
      
  return f"Could not find a clause with the keyword '{keyword}'."

find_clause_by_keyword_tool = FunctionTool(func=find_clause_by_keyword)
