# Legal Document Assistant

This project is a generative AI solution that simplifies complex legal documents into clear, accessible guidance.

## How to run the web application

1.  **Install dependencies:**

    Make sure you are in your virtual environment (`.venv`). Then, install the required libraries:

    ```bash
    pip install fastapi uvicorn python-multipart
    ```

2.  **Run the web server:**

    From the `my-agents` directory, run the following command:

    ```bash
    uvicorn legaldoc_app.web.main:app --host 0.0.0.0 --port 8000
    ```

3.  **Access the application:**

    Open your web browser and go to `http://localhost:8000`.

    You should see the Legal Document Assistant web interface. You can now paste a legal document and start asking questions to the agent.
