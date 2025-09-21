import re
from google.adk.tools import FunctionTool

# Define keywords for each category
KEYWORDS = {
    "Precautions & Cautions": ["caution", "warning", "risk", "liability", "indemnify", "hold harmless", "disclaimer"],
    "Predictions & Suggestions": ["suggest", "recommend", "predict", "forecast", "propose", "advise", "should", "may want to"],
    "Time Limits & Important Dates": ["deadline", "due date", "notice period", "term", "expiration", "effective date", "commencement date"]
}

def summarize_document(document: str) -> str:
    """
    Summarizes a legal document by extracting key information like precautions,
    suggestions, and important dates.

    Args:
        document: The legal document to be summarized.

    Returns:
        A structured summary of the document.
    """
    summary = {
        "Precautions & Cautions": [],
        "Predictions & Suggestions": [],
        "Time Limits & Important Dates": [],
        "Other Key Information": []
    }

    # 1. Find all dates
    # A simple regex for dates (e.g., YYYY-MM-DD, MM/DD/YYYY, Month DD, YYYY)
    date_pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{1,2},?\s\d{4})\b'
    dates = re.findall(date_pattern, document, re.IGNORECASE)
    if dates:
        summary["Time Limits & Important Dates"].extend(f"Date found: {date}" for date in dates)

    # 2. Sentence-based keyword analysis
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', document)
    
    categorized_sentences = set()

    for category, keywords in KEYWORDS.items():
        for sentence in sentences:
            if any(re.search(r'\b' + keyword + r'\b', sentence, re.IGNORECASE) for keyword in keywords):
                if sentence not in categorized_sentences:
                    summary[category].append(sentence.strip())
                    categorized_sentences.add(sentence)

    # 3. Format the output
    output = "### Legal Document Summary\n\n"
    output += "This summary provides a high-level overview of the key points in the document. It is not a substitute for a thorough review of the full document or for legal advice.\n\n"

    for category, items in summary.items():
        if items:
            output += f"--- **{category}** ---\n"
            for item in items:
                output += f"- {item}\n"
            output += "\n"

    if not any(summary.values()):
        return "Could not extract a structured summary from the document. Please review the document carefully."

    return output

summarize_document_tool = FunctionTool(func=summarize_document)
