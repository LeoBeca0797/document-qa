import streamlit as st
import requests
import pdfplumber
import pandas as pd
import json

# Show title and description.
st.title("📄 Document Question Answering")
st.write(
    "Upload a document below and ask a question about it – Gemini will answer! "
    "To use this app, you need to provide a Gemini API key."
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
        # Indicate progress to the user.
        with st.spinner("Processing your request..."):
            try:
                # Extract text from the uploaded file based on its type
                file_type = uploaded_file.name.split(".")[-1].lower()

                if file_type in ["txt", "md"]:
                    document_content = uploaded_file.read().decode()
                elif file_type == "pdf":
                    with pdfplumber.open(uploaded_file) as pdf:
                        document_content = "\n".join(
                            page.extract_text() for page in pdf.pages if page.extract_text()
                        )
                elif file_type == "xlsx":
                    excel_data = pd.read_excel(uploaded_file)
                    document_content = excel_data.to_string(index=False)
                else:
                    st.error("Unsupported file type.")
                    document_content = None

                if not document_content:
                    st.error("The document could not be processed. Please try a different file.")
                    st.stop()

                # Upload the document to Gemini API
                upload_url = "https://generativelanguage.googleapis.com/upload/v1beta/files?uploadType=media"
                headers = {
                    "Authorization": f"Bearer {gemini_api_key}",
                    "Content-Type": "application/pdf" if file_type == "pdf" else "text/plain",
                }
                upload_response = requests.post(
                    upload_url,
                    headers=headers,
                    data=document_content.encode('utf-8'),
                    timeout=30
                )
                upload_response.raise_for_status()
                file_info = upload_response.json()
                file_uri = file_info.get("file", {}).get("uri")

                if not file_uri:
                    st.error("Failed to upload the document.")
                    st.stop

                # Prepare the payload for generating content
                payload = {
                    "prompt": {
                        "context": f"Document URI: {file_uri}",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": question}
                        ]
                    }
                }

                # API endpoint for generating content
                generate_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
                headers = {
                    "Authorization": f"Bearer {gemini_api_key}",
                    "Content-Type": "application/json",
                }

                generate_response = requests.post(
                    generate_url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=30
                )
                generate_response.raise_for_status()
                answer = generate_response.json().get("candidates", [{}])[0].get("output", "No answer found.")

                st.write(f"**Answer:** {answer}")

            except requests.exceptions.Timeout:
                st.error("The request timed out. Please try again later.")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to Gemini API. Please check your network or API URL.")
            except requests.exceptions.HTTPError as http_err:
                st.error(f"HTTP error occurred: {http_err}")
            except requests.exceptions.RequestException as req_err:
                st.error(f"An error occurred: {req_err}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
