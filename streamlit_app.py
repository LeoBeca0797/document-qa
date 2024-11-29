import os
import streamlit as st
import time  # Add time for retry delay
import google.generativeai as genai

# Set up Google Gemini API
st.title("📄 Document Question Answering")
st.write(
    "This app references a pre-existing document `./Document/marcopolo.pdf` "
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

    # Ensure the file exists
    if not os.path.exists(file_path):
        st.error(f"The file 'marcopolo.pdf' does not exist at {file_path}. Please verify its location.")
    else:
        # Ask the user for a question
        question = st.text_area(
            "Now ask a question about the document!",
            placeholder="Can you summarize this document?",
        )

        if question:
            progress = st.progress(0)
            with st.spinner("Processing your request..."):
                try:
                    # Step 1: Upload the file
                    st.info("Step 1: Uploading the document to the Gemini API...")
                    progress.progress(20)

                    uploaded_file_obj = genai.upload_file(
                        path=file_path,
                        mime_type=mime_type,
                        display_name="marcopolo.pdf"
                    )

                    with st.expander("Output of Step 1: Upload Document"):
                        st.json({
                            "uploaded_file_obj.state": uploaded_file_obj.state,
                            "uploaded_file_obj.uri": uploaded_file_obj.uri
                        })

                    # Step 2: Wait for file readiness (retry mechanism)
                    st.info("Checking if the file is ready for processing...")
                    retry_count = 0
                    max_retries = 10  # Set max retries
                    while uploaded_file_obj.state != "ACTIVE" and retry_count < max_retries:
                        time.sleep(2)  # Wait for 2 seconds before retrying
                        uploaded_file_obj = genai.get_file(uploaded_file_obj.uri)  # Re-fetch the file state
                        retry_count += 1

                    if uploaded_file_obj.state != "ACTIVE":
                        st.error("File is still not ready for processing after multiple retries.")
                        progress.progress(100)
                        st.stop()

                    st.success("Step 1: Document is now ready for processing!")
                    progress.progress(50)

                    # Step 3: Generate content
                    st.info("Step 2: Generating content based on the document and your question...")
                    response = genai.generate_content(
                        model="gemini-1.5-pro",
                        prompt=f"Document URI: {uploaded_file_obj.uri}\n\nQuestion: {question}"
                    )

                    with st.expander("Output of Step 2: Generate Content"):
                        st.json(response)

                    st.success("Step 2: Content generation completed!")
                    progress.progress(80)

                    # Step 4: Display the result
                    st.info("Step 3: Displaying the answer...")
                    answer = response.candidates[0]["output"]
                    st.success("Here is the answer:")
                    st.write(f"**Answer:** {answer}")

                    with st.expander("Output of Step 3: Display Result"):
                        st.text(answer)

                    progress.progress(100)

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    progress.progress(100)
