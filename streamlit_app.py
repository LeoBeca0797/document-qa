import streamlit as st
import google.generativeai as genai

# Set up Google Gemini API
st.title("📄 Document Question Answering")
st.write(
    "This app references a pre-existing document located at `/Document/marcopolo.pdf` "
    "and allows you to ask questions about it. "
    "You need to provide a Gemini API key."
)

# Ask the user for their Gemini API key
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please enter your Gemini API key to continue.", icon="🗝️")
else:
    # Configure the Gemini API client
    genai.configure(api_key=gemini_api_key)

    # Pre-defined file path and MIME type
    file_path = "./Document/marcopolo.pdf"
    mime_type = "application/pdf"

    # Ask the user for a question
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you summarize this document?",
    )

    if question:
        with st.spinner("Processing your request..."):
            try:
                # Upload the pre-defined file to the Gemini API
                uploaded_file_obj = genai.upload_file(
                    path=file_path,
                    mime_type=mime_type,
                    display_name="marcopolo.pdf"
                )

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
