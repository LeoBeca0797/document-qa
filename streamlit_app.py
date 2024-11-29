import streamlit as st
import requests

# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below and ask a question about it – Gemini will answer! "
    "To use this app, you need to provide a Gemini API key. "
)

# Ask user for their Gemini API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
    "Upload a document (.txt, .md, .pdf, .xlsx)", type=("txt", "md", "pdf", "xlsx")
)

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        query = {
            "document": document,
            "question": question
        }

        # API endpoint for Gemini's question answering model
        gemini_api_url = "https://api.gemini.ai/v1/question-answering"

        # Send the request to Gemini's API
        headers = {
            "Authorization": f"Bearer {gemini_api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(gemini_api_url, json=query, headers=headers)

        # Check the response status and handle the output
        if response.status_code == 200:
            answer = response.json().get("answer", "No answer found.")
            st.write(f"**Answer:** {answer}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
