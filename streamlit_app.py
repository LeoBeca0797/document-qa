import os
import streamlit as st
import pandas as pd
import pdfplumber
import google.generativeai as genai

# Set up Google Gemini API
st.title("📄 Document Question Answering")
st.write(
    "Upload a document below and ask a question about it – Gemini will answer! "
    "You need to provide a Gemini API key."
)

# Ask the user for their Gemini API key
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please enter your Gemini API key to continue.", icon="🗝️")
else:
    # Configure the Gemini API client
    genai.configure(api_key=gemini_api_key)

    # Let the user upload a file
    uploaded_file = st.file_uploader(
        "Upload a document (.txt, .md, .pdf, .xlsx)", type=("txt", "md", "pdf", "xlsx")
    )

    # Ask the user for a question
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you summarize this document?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        with st.spinner("Processing your request..."):
            try:
                # Process the uploaded file based on its type
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
                    st.error("Could not process the document. Please try a different file.")
                    st.stop()

                # Upload the file to the Gemini API
                temp_file_path = f"/tmp/{uploaded_file.name}"
                with open(temp_file_path, "w", encoding="utf-8") as f:
                    f.write(document_content)

                uploaded_file_obj = genai.upload_file(file_path=temp_file_path)

                if uploaded_file_obj.state != "ACTIVE":
                    st.error("File is not ready for processing.")
                    st.stop()

                # Generate content based on the document and the question
                response = genai.generate_content(
                    model="gemini-1.5-pro",
                    prompt=f"Document URI: {uploaded_file_obj.uri}\n\nQuestion: {question}"
                )

                # Display the generated response
                answer = response.candidates[0]["output"]
                st.success("Here is the answer:")
                st.write(f"**Answer:** {answer}")

            except Exception as e:
                st.error(f"An error occurred: {e}")
