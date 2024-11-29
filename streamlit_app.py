import streamlit as st
import requests
import pdfplumber
import pandas as pd

# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below and ask a question about it – Gemini will answer! "
    "To use this app, you need to provide a Gemini API key. "
)

# Ask user for their Gemini API key via `st.text_input`.
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
        # Process the uploaded file based on its type
        file_type = uploaded_file.name.split(".")[-1].lower()

        try:
            if file_type in ["txt", "md"]:
                document = uploaded_file.read().decode()
            elif file_type == "pdf":
                with pdfplumber.open(uploaded_file) as pdf:
                    document = "\n".join(
                        page.extract_text() for page in pdf.pages if page.extract_text()
                    )
            elif file_type == "xlsx":
                excel_data = pd.read_excel(uploaded_file)
                document = excel_data.to_string(index=False)
            else:
                st.error("Unsupported file type.")
                document = None

            # If document is successfully extracted, process the question
            if document:
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

                # Add timeout and exception handling
                try:
                    response = requests.post(
                        gemini_api_url,
                        json=query,
                        headers=headers,
                        timeout=30  # Timeout in seconds
                    )
                    response.raise_for_status()  # Raise an exception for HTTP errors

                    # Extract and display the answer
                    answer = response.json().get("answer", "No answer found.")
                    st.write(f"**Answer:** {answer}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to Gemini API. Please check your network or API URL.")
                except requests.exceptions.Timeout:
                    st.error("The request timed out. Please try again later.")
                except requests.exceptions.HTTPError as http_err:
                    st.error(f"HTTP error occurred: {http_err}")
                except requests.exceptions.RequestException as req_err:
                    st.error(f"An error occurred: {req_err}")

        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
