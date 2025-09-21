from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="LexiClear API", description="API for simplifying legal documents")

# CORS middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=gemini_api_key)

class ChatRequest(BaseModel):
    question: str
    document: str
def simplify_with_gemini(document_text, question):
    try:
        # Try different model names
        model_names = [
            "gemini-1.0-pro",
            "gemini-pro",
            "models/gemini-pro",
            "gemini-1.5-pro",
            "gemini-1.0-pro-001"
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                prompt = f"""
                You are a legal expert who simplifies complex legal documents into plain English.
                
                Question: {question}
                
                Please analyze the following legal document and provide a clear, easy-to-understand explanation.
                
                Document:
                {document_text}
                
                Provide a simplified explanation that covers:
                1. The main purpose of the document
                2. Key terms and what they mean in plain language  
                3. Important obligations or rights mentioned
                4. Any potential risks or considerations
                5. Overall summary
                
                Write in a friendly, accessible tone suitable for someone without legal training.
                Keep your response under 500 words.
                """

                response = model.generate_content(prompt)
                return response.text
                
            except Exception as e:
                print(f"Tried model {model_name}, error: {e}")
                continue
        
        raise Exception("None of the model names worked")
        
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"Processing request with Gemini for document length: {len(request.document)}")
        
        # Use Google Gemini for simplification
        simplified_text = simplify_with_gemini(request.document, request.question)
        
        return {"response": simplified_text}
    
    except Exception as e:
        print(f"Error in chat_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/")
async def read_root():
    try:
        with open("index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except FileNotFoundError:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LexiClear - Legal Document Simplifier</title>
        </head>
        <body>
            <h1>LexiClear API</h1>
            <p>Legal Document Simplification API is running with Google Gemini.</p>
            <p>Use the /chat endpoint to simplify legal documents.</p>
        </body>
        </html>
        """
        return HTMLResponse(html_content)